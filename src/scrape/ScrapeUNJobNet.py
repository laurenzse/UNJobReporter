import html2text
import requests
import json
import re
from tqdm import tqdm

from src.scrape.ScrapeIOMJobDescription import get_iom_job_description
from src.data.Job import UNJobStub, UNJob

h = html2text.HTML2Text()


def load_full_job(un_job_stub: UNJobStub):
    return UNJob(
        un_job_stub.un_jobnet_id,
        un_job_stub.title,
        un_job_stub.department,
        un_job_stub.grade,
        un_job_stub.level,
        un_job_stub.cities_countries,
        un_job_stub.job_type,
        un_job_stub.organization_short_name,
        un_job_stub.organization_long_name,
        un_job_stub.date_posted,
        un_job_stub.updated,
        un_job_stub.deadline,
        un_job_stub.recruitment_place,
        _fetch_job_description(un_job_stub),
        {},
    )


def _fetch_job_description(job_stub: UNJobStub) -> str:
    jobnet_detail_url = f"https://www.unjobnet.org/jobs/detail/{job_stub.un_jobnet_id}"
    page = requests.get(jobnet_detail_url)

    # if organization is IOM, we cannot scrape directly in most cases
    # but need to visit their website, download a pdf and extract the description from there
    if (
        job_stub.organization_short_name == "IOM"
        and "View on Organization Website" in page.text
    ):
        return get_iom_job_description(job_stub.title)

    # use trafilatura to extract the main content of the job detail page which is the job description
    all_page_content = h.handle(page.text)

    # get content between "Job Description" and "Similar Jobs" using regex
    pattern = r"\nJob Description([\s\S]*?)Similar Jobs"

    return re.search(pattern, all_page_content).group(1)


def _extract_json_from_html(html_code):
    # Regular expression pattern to find the JSON data structure
    pattern = r"jobs :\s*\[([\s\S]*?)}]"

    # Search for the pattern in the input HTML code
    match = re.search(pattern, html_code)

    if not match:
        # If no match is found, return None
        return None

    # Extract the JSON data structure from the match, including the square brackets
    json_data_with_brackets = "[" + match.group(1) + "}]"

    try:
        # Load the JSON data as a Python dictionary
        extracted_data = json.loads(json_data_with_brackets)
    except json.JSONDecodeError:
        # If JSON decoding fails, return None
        return None

    return extracted_data


def load_new_job_stubs_at_url(
    url: str, until_page: int, seen_jobs: set[str]
) -> list[UNJob]:
    # url ends with page number, e.g. https://www.unjobnet.org/jobs?occupations%5B0%5D=6&levels%5B0%5D=1&page=1
    # we need to remove the page number to be able to iterate over all pages
    url_base = url[:-1]

    job_stubs = []

    for page_number in range(1, until_page + 1):
        print(f"Fetching page {page_number} of {until_page}...")
        page = requests.get(url_base + str(page_number))

        # Extract JSON data from the HTML code
        extracted_data = _extract_json_from_html(page.text)

        if not extracted_data:
            print("No JSON data found.")
            continue

        # convert JSON jobs into UNJobStub objects
        new_job_stubs = [UNJobStub.create_from_dict(job) for job in extracted_data]

        # filter for all jobs which we have not seen before
        new_job_stubs = [
            job for job in new_job_stubs if job.un_jobnet_id not in seen_jobs
        ]
        seen_jobs.update([job.un_jobnet_id for job in new_job_stubs])

        job_stubs.extend(new_job_stubs)

    return job_stubs


def load_jobs_from_job_stubs(job_stubs: list[UNJobStub]) -> list[UNJob]:
    # convert UNJobStub objects into UNJob objects (downloads job descriptions and might take a while)
    jobs = [load_full_job(job) for job in tqdm(job_stubs)]

    return jobs
