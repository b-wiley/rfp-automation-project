# RFP Automation Project

At Census, prospective customers typically like to kick off the technical and commercial evaluation process by creating an Excel sheet full of requirements, to better guage which vendors are going to be a good fit, prior to actually talking to them. This is very common.  It is our jobs as Solutions Engineers and Account Executives to go through each requirement and provide a response to each requirement.  As a team, we manually go through each requirement by explaining whether or not we can meet a requirement, as well as some additional information about how we meet the requirement.

### What is an RFP?
For context, an RFP (Request for Proposal) is a formal document issued by an organization to solicit proposals from qualified vendors for a specific product or service. It outlines the project's requirements, goals, and the organization's needs, enabling potential vendors to understand the scope of work and submit proposals that best meet the organization's objectives. This competitive process helps organizations find the most suitable solution by allowing them to compare proposals from various vendors based on factors like price, experience, and proposed solutions.

### Why automate this process?
I have personally worked on RFPs that have been up to 500 requirements.  This means that as a team, we will collectively spend days and weeks thoroughly going through the document to ensure we're putting our best foot forward as a company, while being fully transparent with what we can and cannot support.  Every RFP we complete is another manual task that we complete, which becomes very repetitive as our answers rarely change.  (Answers only change when the product or commercial terms change).

This means that there is a glaring opportunity for us to save countless hours by automating this process and Generative AI is the perfect solution!  There are plenty of SaaS tools out there that do this themselves, but this is simple enough of a feature that I believe is worth automating in-house.

--------

### How this works

The goal of this project is to take any arbitrary RFP that myself or my team has filled out over the last 6 months and use that to fine-tune an OpenAI model with the goal of achieving two things froma fine-tuned model: accurate answers and answers that are written how we write.

There are several components to this project, as there are several steps that need to be completed before we can even generate accurate answers:

1. Transform Data (`transform_data_for_fine_tuning.py`) - Prior to fine-tuning an OpenAI model, we need to ensure that our data is in the correct format.  In this case, our data is going to come from historical RFPs that we've filled out.  So, regardless of the shape of the RFP (they're always in different formats), we need to ensure that we're taking the correct columns and mapping them to the right parameters for OpenAI's fine-tuning endpoint.  In this case, we are taking data from a .csv format and transforming the data into a JSONL payload which is what OpenAI asks for (https://platform.openai.com/docs/guides/fine-tuning).  We're then going to store this somewhere (locally for now) prior to fine-tuning.
2. Fine-tune Model (`fine_tune_open_ai.py`) - Once we have data in the right format, we are going to then select the newly created JSONL file and upload that file into OpenAI so that we can obtain a `file_id`.  Then, once we have the `file_id`, we will fine-tune an OpenAI model using our data.  In this case, I have decided to use the following model: `GPT-4o-mini-2024-07-18`.  
