import json
import os

from src.enrich.GenerateOpenAIFunction import generate_summaries

test_url = "https://www.unjobnet.org/jobs?occupations%5B0%5D=6&levels%5B0%5D=Entry+Professional&keywords=&locations%5B0%5D=&orderby=recent&page=1"

questions = ["Summarize the job duties and the broader context of the job in two sentences. "
             "Do not repeat the job title or otherwise name the job, e.g. start your sentence with the verb.",
             "What is the long-term vision for the project this job relates to?",
             "Which technologies are used in this job?",
             "Are certain nationalities preferred?",
             "What are the language requirements of this job?",
             "How many years of experience are required?"]

if __name__ == '__main__':
    # ask user for urls that should be crawled until empty string is entered
    print("Please enter the URLs of the UNJobNet job search pages you want to crawl. Make sure you enabled sorting by most recent. Press enter to finish.")
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

    # ask for email address to which the report should be sent
    print("Please enter the email address to which the report should be sent.")
    email = input("Email: ")

    # generate summaries of quesions
    summaries = generate_summaries(questions)

    # create file named "seen_jobs.csv", if file exists, append number to file name
    file_name = "seen_jobs.csv"
    i = 1
    while os.path.exists(file_name):
        file_name = f"seen_jobs_{i}.csv"
        i += 1
    with open(file_name, 'w') as f:
        f.write("")

    # write url and summaries to config file
    config_file = {'urls': urls, 'summaries': summaries, 'seen_job_file': file_name, 'email': email}

    # write config file
    with open("config.json", 'w') as f:
        # pretty print json
        json.dump(config_file, f, indent=4)


