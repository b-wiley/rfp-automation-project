"""Turn one or more completed RFP CSVs into the JSONL training file OpenAI fine-tuning expects.

Example:
    python transform_data_for_fine_tuning.py past_rfp_1.csv past_rfp_2.csv -o training.jsonl \
        --question-col Requirement --answer-col Response
"""

import argparse
import json

from rfp_common import ANSWER_SYSTEM_PROMPT, choose_column, read_csv


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_files", nargs="+", help="Completed RFP CSV file(s)")
    parser.add_argument("-o", "--output", default="training.jsonl", help="Output JSONL path")
    parser.add_argument("--question-col", help="Question column name (asked interactively if omitted)")
    parser.add_argument("--answer-col", help="Answer column name (asked interactively if omitted)")
    args = parser.parse_args()

    written = skipped = 0
    seen = set()
    with open(args.output, "w", encoding="utf-8") as out:
        for csv_file in args.csv_files:
            rows, fieldnames = read_csv(csv_file)
            print(f"\n{csv_file}: {len(rows)} rows")
            q_col = choose_column(fieldnames, "question", args.question_col)
            a_col = choose_column(fieldnames, "answer", args.answer_col)

            for row in rows:
                question = (row.get(q_col) or "").strip()
                answer = (row.get(a_col) or "").strip()
                # Skip blank rows and exact duplicates (the same requirement shows up across many RFPs).
                if not question or not answer or (question, answer) in seen:
                    skipped += 1
                    continue
                seen.add((question, answer))

                example = {
                    "messages": [
                        {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer},
                    ]
                }
                out.write(json.dumps(example, ensure_ascii=False) + "\n")
                written += 1

    print(f"\nWrote {written} training examples to {args.output} (skipped {skipped} blank or duplicate rows).")
    if written < 10:
        print("Warning: OpenAI requires at least 10 examples to fine-tune.")


if __name__ == "__main__":
    main()
