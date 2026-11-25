"""Fill in an RFP CSV with answers from the fine-tuned model.

Requests run in parallel, so a 500-row RFP takes about a minute instead of tens of minutes.
Answers are written to a new file; the original is never overwritten.

Reads your key from OPENAI_API_KEY, and the fine-tuned model name from --model or RFP_MODEL.

Example:
    python rfp_automation.py new_rfp.csv --model ft:gpt-4o-mini-2024-07-18:census:census-rfp:abc123
"""

import argparse
import asyncio
import os
import sys

from openai import AsyncOpenAI

from rfp_common import (
    ANSWER_SYSTEM_PROMPT,
    BASE_MODEL,
    REFORMAT_SYSTEM_PROMPT,
    choose_column,
    default_output_path,
    read_csv,
    write_csv,
)


async def ask(client, limiter, model, system_prompt, text):
    async with limiter:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.2,  # low temperature keeps answers consistent from run to run
        )
        return response.choices[0].message.content.strip()


async def process_row(client, limiter, args, requirement, progress):
    try:
        # Requirements already phrased as questions skip the rewrite call.
        if args.no_reformat or requirement.endswith("?"):
            question = requirement
        else:
            question = await ask(client, limiter, BASE_MODEL, REFORMAT_SYSTEM_PROMPT, requirement)
        answer = await ask(client, limiter, args.model, ANSWER_SYSTEM_PROMPT, question)
    except Exception as e:  # one bad row shouldn't sink the whole RFP
        answer = f"ERROR: {e}"
    progress["done"] += 1
    print(f"\r  {progress['done']}/{progress['total']} answered", end="", flush=True)
    return answer


async def run(args):
    rows, fieldnames = read_csv(args.csv_file)
    q_col = choose_column(fieldnames, "question", args.question_col)
    a_col = choose_column(fieldnames, "answer", args.answer_col)

    # Only answer rows that have a requirement and don't already have an answer.
    todo = [
        i for i, row in enumerate(rows)
        if (row.get(q_col) or "").strip() and (args.overwrite or not (row.get(a_col) or "").strip())
    ]
    if not todo:
        sys.exit("Nothing to answer: every row is blank or already has an answer (use --overwrite to redo them).")

    print(f"\nAnswering {len(todo)} of {len(rows)} rows with {args.model} ({args.concurrency} at a time)...")
    client = AsyncOpenAI(max_retries=5)  # retries rate-limit and network errors with backoff
    limiter = asyncio.Semaphore(args.concurrency)
    progress = {"done": 0, "total": len(todo)}

    answers = await asyncio.gather(
        *(process_row(client, limiter, args, rows[i][q_col].strip(), progress) for i in todo)
    )

    for i, answer in zip(todo, answers):
        rows[i][a_col] = answer

    output = args.output or default_output_path(args.csv_file, "answered")
    write_csv(output, rows, fieldnames)
    errors = sum(a.startswith("ERROR:") for a in answers)
    print(f"\n\nWrote answers to {output}" + (f" ({errors} rows failed; search for 'ERROR:')" if errors else ""))
    print("Review every answer before sending the RFP.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_file", help="RFP CSV to fill in")
    parser.add_argument("--model", default=os.environ.get("RFP_MODEL"), help="Fine-tuned model name")
    parser.add_argument("--question-col", help="Question column name (asked interactively if omitted)")
    parser.add_argument("--answer-col", help="Answer column name (asked interactively if omitted)")
    parser.add_argument("-o", "--output", help="Output CSV path (default: <input>_answered.csv)")
    parser.add_argument("--concurrency", type=int, default=10, help="Parallel requests (default 10)")
    parser.add_argument("--no-reformat", action="store_true", help="Skip rewriting requirements as questions")
    parser.add_argument("--overwrite", action="store_true", help="Also redo rows that already have an answer")
    args = parser.parse_args()

    if not args.model:
        sys.exit("Set the fine-tuned model with --model or the RFP_MODEL environment variable.")
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
