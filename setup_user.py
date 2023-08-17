import json
import os

from src.enrich.GenerateOpenAIFunction import generate_summaries

test_url = "https://www.unjobnet.org/jobs?occupations%5B0%5D=6&levels%5B0%5D=Entry+Professional&keywords=&locations%5B0%5D=&orderby=recent&page=1"

questions = [
    "Summarize the job duties and the broader context of the job in two sentences. "
    "Do not repeat the job title or otherwise name the job, e.g. start your sentence with the verb.",
    "What is the long-term vision for the project this job relates to?",
    "Which technologies are used in this job?",
    "Are certain nationalities preferred?",
    "What are the language requirements of this job?",
    "How many years of experience are required?",
]

if __name__ == "__main__":
    # ask user for urls that should be crawled until empty string is entered
    print(
        "Please enter the URLs of the UNJobNet job search pages you want to crawl. Make sure you enabled sorting by most recent. Press enter to finish."
    )
    urls = []
    while True:
        url = input("URL: ")
        if url == "":
            break
        urls.append(url)

    # ask for questions
    # print("Please enter the questions you want to ask about each job. Press enter to finish.")
    # questions = []
    # while True:
    #     question = input("Question: ")
    #     if question == "":
    #         break
    #     questions.append(question)

    # ask for continents which should be filtered out
    print(
        "Please enter the continent codes (e.g. EU, AF, SA) you want to filter out. Press enter to finish."
    )
    continents = []
    while True:
        continent = input("Continent: ")
        if continent == "":
            break
        continents.append(continent)

    # ask for email address to which the report should be sent
    print("Please enter the email address to which the report should be sent.")
    email = input("Email: ")

    # generate summaries of quesions
    summaries = generate_summaries(questions)

    # generate id out of email address by replacing all non-alphanumeric characters with underscores
    email_id = "".join([c if c.isalnum() else "_" for c in email])

    # create seen_jobs file with file name including email id
    seen_jobs_filename = f"seen_jobs_{email_id}.csv"
    open(seen_jobs_filename, "w").close()

    # create config file content
    config_file = {
        "email_id": email_id,
        "email": email,
        "urls": urls,
        "summaries": summaries,
        "continent_filter": continents,
    }

    # write config file
    with open(f"{email_id}.json", "w") as f:
        # pretty print json
        json.dump(config_file, f, indent=4)

    # print file name of config file to user and instruct how to use it with main.py
    print(
        f"Config file {email_id}.json created. Call main.py with this file as argument to start the crawler."
    )
