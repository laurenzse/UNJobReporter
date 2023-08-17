from dataclasses import dataclass, asdict
from jinja2 import Environment, FileSystemLoader

from src.data.Job import UNJob


@dataclass
class UnreportedJob:
    url: str
    title: str


@dataclass
class JobReport:
    url: str
    title: str
    table_data: dict[str, str]
    detailed_data: dict[str, str]


@dataclass
class JobEmail:
    first_sentence: str
    unreported_jobs: list[UnreportedJob]
    job_reports: list[JobReport]

    def as_dict(self):
        return {k: v for k, v in asdict(self).items()}


def create_html_for_job_email(job_email: JobEmail):
    environment = Environment(loader=FileSystemLoader("src/report/template"))
    template = environment.get_template("email_template.html")

    content = template.render(job_email.as_dict())
    return content


def get_job_report_for_job(job: UNJob):
    jobnet_detail_url = f"https://www.unjobnet.org/jobs/detail/{job.un_jobnet_id}"

    # parse deadline to datetime and create deadline string in this format: "August 8"
    deadline_str = (
        job.deadline.strftime("%B %d") if job.deadline is not None else "Unknown"
    )

    # get location, orgnaization, job type and deadline
    table_data = {
        "Location": job.cities_countries,
        "Organization": job.organization_short_name,
        "Job Type": job.job_type,
        "Deadline": deadline_str,
    }

    # check if there is a detailed description, otherwise include hint that description could not be procesed
    if job.questions_and_answers is None or len(job.questions_and_answers) == 0:
        detailed_data = {"Could not process description.": ""}
    else:
        detailed_data = job.questions_and_answers

    return JobReport(jobnet_detail_url, job.title, table_data, detailed_data)


def construct_email_report_html(jobs: list[UNJob]):
    general_descprition = "Found {} new jobs.".format(len(jobs))
    unreported_jobs = []
    job_reports = [get_job_report_for_job(job) for job in jobs]

    job_email = JobEmail(general_descprition, unreported_jobs, job_reports)

    return create_html_for_job_email(job_email)
