import json
import openai
import os

from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ["OPENAI_API_KEY"]

summary_function = {
    "name": "set_prompt_summary",
    "description": "Sets the summary of a question or request.",
    "parameters": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "An extremely short summary of the question or request, maximum 3 words.",
            },
        },
        "required": ["summary"],
    },
}


def get_prompt_summary(prompt: str) -> str:
    prompt = f"""
    A user has submitted this request or question:
    
    {prompt}
    
    Please generate a summary of this request or question which will be displayed to the user 
    above the answer to the question. The summary should be a maximum of 3 words as space is limited. 
    
    Please return a JSON object as the result.
    """
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful UI optimization assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        functions=[summary_function],
    )
    try:
        generated_text = completion.choices[0].message.function_call.arguments
        return json.loads(generated_text)["summary"]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def generate_summaries(prompts: list) -> dict:
    summaries = {}
    for prompt in prompts:
        summary = get_prompt_summary(prompt)
        summaries[prompt] = summary
    return summaries


def get_question_function(summaries: dict):
    # generate properties out of each question and summary
    properties = {}
    for question, summary in summaries.items():
        properties[summary] = {"type": "string", "description": question}

    required = list(properties.keys())

    # generate the function
    summary_function = {
        "name": "answer_job_request",
        "description": "Sets the answers for questions and requests about a job description.",
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }

    return summary_function
