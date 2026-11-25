"""Upload a JSONL training file and start an OpenAI fine-tuning job.

Reads your key from the OPENAI_API_KEY environment variable.

Example:
    python fine_tune_open_ai.py training.jsonl --wait
"""

import argparse
import time

from openai import OpenAI

from rfp_common import BASE_MODEL


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("training_file", help="JSONL file from transform_data_for_fine_tuning.py")
    parser.add_argument("--model", default=BASE_MODEL, help=f"Base model to fine-tune (default {BASE_MODEL})")
    parser.add_argument("--suffix", default="census-rfp", help="Label added to the fine-tuned model's name")
    parser.add_argument("--wait", action="store_true", help="Wait for the job to finish and print the model name")
    args = parser.parse_args()

    client = OpenAI()

    with open(args.training_file, "rb") as f:
        uploaded = client.files.create(file=f, purpose="fine-tune")
    print(f"Uploaded file: {uploaded.id}")

    job = client.fine_tuning.jobs.create(training_file=uploaded.id, model=args.model, suffix=args.suffix)
    print(f"Started fine-tuning job: {job.id}")

    if not args.wait:
        print("Run again with --wait, or check the job in the OpenAI dashboard.")
        return

    while job.status not in ("succeeded", "failed", "cancelled"):
        time.sleep(30)
        job = client.fine_tuning.jobs.retrieve(job.id)
        print(f"  status: {job.status}")

    if job.status == "succeeded":
        print(f"\nFine-tuned model: {job.fine_tuned_model}")
        print("Pass it to rfp_automation.py with --model, or set RFP_MODEL to it.")
    else:
        print(f"\nJob ended with status '{job.status}': {job.error}")


if __name__ == "__main__":
    main()
