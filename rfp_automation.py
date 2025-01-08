from openai import OpenAI #type:ignore
import csv
import sys

# OpenAI Credentials
client = OpenAI(
  organization='org-xxxxxx',
  project='proj_xxxxxxx',
  api_key = '**************'
)

def designate_columns(rows):
    keys = list(rows[0].keys())
    i = 0
    columns_options = {}
    question_column = ""
    answer_column = ""

# --------------------------------------------------------
    print("--------------------------------------------------------------------")
    print()
    print("Below are the columns in the uploaded set of data.")
    while i < len(keys):
        print(f"{i}) {keys[i]}")
        columns_options[i] = keys[i]
        i += 1
    print("--------------------------------------------------------------------")

# --------------------------------------------------------
    question_column_number_selection = input("Please select the number that corresponds to the question column: ")
    for nums in columns_options.keys():
        if nums == int(question_column_number_selection):
            question_column = columns_options[int(question_column_number_selection)]
            print(f"Question Column Selected: {question_column}")

    if not question_column:
        print("Invalid selection made, ending program.  Please retry.")
        sys.exit()
    print()

# --------------------------------------------------------
    answer_column_number_selection = input("Please select the number that corresponds to the answer column: ")
    for nums in columns_options.keys():
        if nums == int(answer_column_number_selection):
            answer_column = columns_options[int(answer_column_number_selection)]
            print(f"Answer Column Selected: {answer_column}")

    if not question_column:
        print("Invalid selection made, ending program.  Please retry.")
        sys.exit()
    
    print("--------------------------------------------------------------------")
    print()
    return question_column, answer_column

def format_questions(rows, question_column):
    reformatted_questions_obj = {}
    #reformatting_prompt = 'Your task is to take a requirement laid out by a prospective customer and turn the requirement into a question. The context is that a prospective customer is looking to learn more about the capabilities of Census (www.getcensus.com). Typically the question is going to revolve around asking if Census supports a given feature or if Census has a given integration.  For example, here is a requirement: "Support Databricks as a source". The output of the question should then be:  "Does Census support Databricks as a source integration?"'
    reformatting_prompt = """
        Your task is to take a requirement laid out by a prospective customer and turn the requirement into a question. The context is that a prospective customer is looking to learn more about the capabilities of Census (www.getcensus.com).
        Typically the question is going to revolve around asking if Census supports a given feature or if Census has a given integration.
        For example, here is a requirement: "Support Databricks as a source". The output of the question should then be:  "Does Census support Databricks as a source integration?"
    """
    i=0
    while i < len(rows):
        completion = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "developer", "content": reformatting_prompt},
                {"role": "user", "content": rows[i][question_column]}
            ]
        )

        new_question = completion.choices[0].message.content
        reformatted_questions_obj[i] = {
            "original_question": rows[i][question_column],
            "reformatted_question": new_question
        }
        i+=1

    print("--------------------------------------------------------------------")
    print("Questions have been generated!  Moving on to generate answers step.  Stand by.....")
    print("--------------------------------------------------------------------")
    print()
    return reformatted_questions_obj


def generate_answers(rows, reformatted_questions_obj):
    questions_answered_obj = reformatted_questions_obj
    generate_answers_prompt = """
        You are a knowledgeable and helpful assistant designed to provide precise, accurate, and user-centric answers to questions. Your primary resource for context and guidance is the Census Documentation. When answering questions:
            1) Prioritize Information: Always refer to the Census Documentation for accurate, up-to-date information. If the documentation doesn't cover the query, draw upon general knowledge while clearly indicating the source.
            2) Clarity and Relevance: Ensure your responses are concise, clear, and directly relevant to the user's question. Avoid overloading with unnecessary details.
            3) Polite and Professional Tone: Maintain a courteous, professional tone in all responses, ensuring a positive user experience.
            4) Handling Unavailable Information: If a question falls outside the scope of available resources or expertise, kindly inform the user and suggest consulting the Census support team or alternative resources.
        Your goal is to assist users effectively by leveraging the best available information and providing well-structured, insightful answers. 
        Additionally, each answer should elaborate in the form of 2-3 full sentences with as much information as possible.
    """
    
    i=0

    # while loop
    while i < len(questions_answered_obj):
        completion = client.chat.completions.create(
            # Fine-tuned model
            model="*****",
            messages=[
                {"role": "developer", "content": generate_answers_prompt},
                {"role": "user", "content": questions_answered_obj[i]['reformatted_question']}
            ]
        )
        questions_answered_obj[i]["generated_answer"] = completion.choices[0].message.content
        i+=1
    
    print("--------------------------------------------------------------------")
    print("Answers have been generated!  Writing answers back into the orignal CSV file.  Stand by.....")
    print("--------------------------------------------------------------------")
    print()
    return questions_answered_obj

def write_to_csv(rows, answer_column, questions_answered_obj, csv_file, reader):
    for i, row in enumerate(rows):
        row[answer_column] = questions_answered_obj[i]['generated_answer']

    with open(csv_file, mode='w', newline='') as file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(rows)

    print("--------------------------------------------------------------------")
    print("CSV file has been updated with the generated answers!")
    print("--------------------------------------------------------------------")
    print()
    return


def main():
    # CSV file location
    csv_file = "***"
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    [question_column, answer_column] = designate_columns(rows)
    reformatted_questions_obj = format_questions(rows, question_column)
    questions_answered_obj = generate_answers(rows, reformatted_questions_obj)
    write_to_csv(rows, answer_column, questions_answered_obj, csv_file, reader)

main()