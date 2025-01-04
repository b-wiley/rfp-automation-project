from openai import OpenAI #type:ignore
import csv
import json
import sys

# Still a work in progress!


reformatting_prompt = 'Your task is to take a requirement laid out by a prospective customer and turn the requirement into a question. The context is that a prospective customer is looking to learn more about the capabilities of Census (www.getcensus.com). Typically the question is going to revolve around asking if Census supports a given feature or if Census has a given integration.  For example, here is a requirement: "Support Databricks as a source". The output of the question should then be:  "Does Census support Databricks as a source integration?"'

# CSV file location
csv_file = ""

with open(csv_file, "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)



def designate_columns(rows):
    keys = list(rows[0].keys())
    i = 0
    columns_options = {}
    question_column = ""
    answer_column = ""
# --------------------------------------------------------
    print("----------------------------------")
    print("Below are the columns in the uploaded set of data.")
    while i < len(keys):
        print(f"{i}) {keys[i]}")
        columns_options[i] = keys[i]
        i += 1
    print("----------------------------------")
# --------------------------------------------------------
    question_column_number_selection = input("Please select the number that corresponds to the question column: ")
    for nums in columns_options.keys():
        if nums == int(question_column_number_selection):
            question_column = columns_options[int(question_column_number_selection)]
            print(f"Question Column Selected: {question_column}")

    if not question_column:
        print("Invalid selection made, ending program.  Please retry.")
        sys.exit()
# --------------------------------------------------------
    answer_column_number_selection = input("Please select the number that corresponds to the answer column: ")
    for nums in columns_options.keys():
        if nums == int(answer_column_number_selection):
            answer_column = columns_options[int(answer_column_number_selection)]
            print(f"Answer Column Selected: {answer_column}")

    if not question_column:
        print("Invalid selection made, ending program.  Please retry.")
        sys.exit()

    return question_column, answer_column

def format_questions(rows, question_column):
    print(rows[0][question_column])


def main(rows):
    [question_column, answer_column] = designate_columns(rows)
    format_questions(rows, question_column)

main(rows)
