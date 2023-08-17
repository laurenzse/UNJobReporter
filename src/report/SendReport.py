import os
import resend
from dotenv import load_dotenv

from src.report.ComposeEmailHtml import construct_email_report_html
from src.data.Job import UNJob

load_dotenv()
resend.api_key = os.environ["RESEND_API_KEY"]


def send_job_email(jobs: list[UNJob], email_recipient: str):
    job_email_html = construct_email_report_html(jobs)

    r = resend.Emails.send(
        {
            "from": "Job Notifications <job-notifications@laurenzseidel.com>",
            "to": email_recipient,
            "subject": "UN Job Report",
            "html": job_email_html,
        }
    )
