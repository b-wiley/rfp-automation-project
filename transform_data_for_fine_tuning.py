# The goal of this python script is to intake a csv file, parse through each row to obtain questions & answers, then
# insert those questions and answers into the required payload format, which then gets stored as a JSONL file format.
# OpenAI's Fine-Tuning endpoint requires that the file structure be formatted as a JSONL.  OpenAI also requires the
# payload be structured in a certain format, which is why this script exists.

import csv
import json

# Prompt that will be used to provide context for training
prompt = ""
# Required roles for OpenAI fine-tuning endpoint
roles = ["system","user","assistant"]

# CSV file location
csv_file = ""
# Desired JSONL file output location
jsonl_file = ""

question_column = ''
answer_column = '='

# Read CSV file and assign to vairable "rows"
with open(csv_file, "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)


# Templatize the reequired OpenAI fine tuning payload format
# Loop through each row in the CSV and write the payload to the JSONL file
# Automatically dump each new JSONL row into the output file
def main(rows, roles, prompt, jsonl_file, question_column, answer_column):
    with open(jsonl_file, mode='w', encoding='utf-8') as jsonl_file:
      payload = {
        "messages": [
            {
                "role": roles[0],
                "content": prompt
            },
            {
                "role": roles[1], 
                "content": ""
            },
            {
                "role": roles[2],
                "content": ""
            }
        ]
      }

      for row in rows:
          question = row[question_column]
          answer = row[answer_column]

          payload.copy()

          payload["messages"][1]["content"] = question + "?"
          payload["messages"][2]["content"] = answer

          jsonl_file.write(json.dumps(payload) + '\n')

    print("File transformed.")

main(rows, roles, prompt, jsonl_file, question_column, answer_column)