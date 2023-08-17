import json
from tqdm import tqdm

from src.enrich.EnrichJob import answer_job_questions
from src.enrich.GenerateOpenAIFunction import get_question_function, generate_summaries
from src.filter.RawFilter import filter_jobs
from src.report.SendReport import send_job_email
from src.scrape.ScrapeUNJobNet import (
    load_new_job_stubs_at_url,
    load_jobs_from_job_stubs,
)


def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
        return config


def load_seen_jobs(config: dict) -> set[str]:
    with open(config["seen_job_file"], "r") as f:
        seen_jobs = set(f.read().splitlines())
        return seen_jobs


fetch_pages = 4

if __name__ == "__main__":
    # 1) load config and seen jobs
    config = load_config()
    seen_jobs = load_seen_jobs(config)

    # 2) get new jobs
    job_stubs = []
    for url in config["urls"]:
        new_job_stubs = load_new_job_stubs_at_url(url, fetch_pages, seen_jobs)
        job_ids = [job_stub.un_jobnet_id for job_stub in new_job_stubs]

        # add to seen_jobs
        seen_jobs.update(job_ids)

        job_stubs.extend(new_job_stubs)

    # 3) filter jobs
    job_stubs, denied_stubs = filter_jobs(job_stubs)

    # check if there are new jobs
    if len(job_stubs) == 0:
        print("No new jobs found.")
        exit(0)

    job_stubs = job_stubs[:1]

    # 3) load full jobs
    jobs = load_jobs_from_job_stubs(job_stubs)

    # 4) answer questions about jobs
    summaries = config["summaries"]
    question_function = get_question_function(summaries)

    for job in tqdm(jobs):
        question_and_answers = answer_job_questions(job, question_function)
        job.questions_and_answers = question_and_answers

    # 5) send job report via email
    send_job_email(jobs, config["email"])

    # 6) save seen jobs
    with open(config["seen_job_file"], "a") as f:
        for job in jobs:
            f.write(job.un_jobnet_id + "\n")
