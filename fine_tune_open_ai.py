from openai import OpenAI #type:ignore
import time

# OpenAI Credentials
client = OpenAI(
  organization='org-xxxxxx',
  project='proj_xxxxxxx',
  api_key = '**************'
)

# Structured JSONL file location
file_location = "/file/location/xxxxxx"

# OpenAI model to be fine-tuned
model_for_tuning = ""

# Function used to upload JSONL files to OpenAI
def upload_file(client, file_location):
    upload_file_job = client.files.create(
        file=open(file_location, "rb"),
        purpose="fine-tune"
    )

    file_id = upload_file_job.id
    return file_id

# Function used to take the file ID from the previous step and fine-tune the specified model
def init_ft_job(client, file_id, model_for_tuning):
    fine_tuning_job = client.fine_tuning.jobs.create(
        training_file = file_id,
        model = model_for_tuning
    )

    print(fine_tuning_job)

# Main function that runs each step function
def main(client, file_location, model_for_tuning):
    file_id = upload_file(client, file_location)
    print(f"FILE ID: {file_id}")
    time.sleep(5)
    init_ft_job(client, file_id, model_for_tuning)

# Execute Script
main(client, file_location, model_for_tuning)