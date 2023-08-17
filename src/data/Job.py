import re
from dataclasses import dataclass
from datetime import datetime


@dataclass
class UNJobStub:
    un_jobnet_id: str
    title: str
    department: str
    grade: str
    level: str
    cities_countries: str
    job_type: str
    organization_short_name: str
    organization_long_name: str
    date_posted: datetime
    updated: datetime
    deadline: datetime
    recruitment_place: str

    @classmethod
    def create_from_dict(cls, job_dict: dict):
        date_posted = cls._parse_date_str(job_dict["DatePosted"])
        updated = cls._parse_date_str(job_dict["Updated"])

        if job_dict["Deadline"] != "":
            deadline = cls._parse_deadline(job_dict["Deadline"])
        else:
            deadline = None

        return UNJobStub(
            job_dict["JobID"],
            job_dict["Title"],
            job_dict["Department"],
            job_dict["Grade"],
            job_dict["Level"],
            job_dict["CitiesCountries"],
            job_dict["AppType"],
            job_dict["ShortName"],
            job_dict["LongName"],
            date_posted,
            updated,
            deadline,
            job_dict["RecruitmentPlace"],
        )

    @staticmethod
    def _parse_deadline(deadline_str: str) -> datetime:
        # deadline might be given in strings in either this format
        # "'<span class="">Close on 17 Aug 2023</span>'"
        # or this format
        # "'<span class="text-danger font-weight-bold">Closing soon: 9 Aug 2023</span>'"

        # 1) extract the date string
        regex_str = r"\b(?:\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4})\b"
        deadline_date_str = re.findall(regex_str, deadline_str)[0]

        # 2) convert it to a datetime object
        deadline_date = datetime.strptime(deadline_date_str, "%d %b %Y")

        return deadline_date

    @staticmethod
    def _parse_date_str(date_str: str) -> datetime:
        # date strings are given in this format
        # "'2023-07-28 11:50:05'"

        # convert it to a datetime object
        datetime_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        return datetime_date


@dataclass
class UNJob(UNJobStub):
    description: str
    questions_and_answers: dict[str, str]

    def serialize(self):
        # return dict with all attributes but datetime objects as strings
        return {
            "un_jobnet_id": self.un_jobnet_id,
            "title": self.title,
            "department": self.department,
            "grade": self.grade,
            "level": self.level,
            "cities_countries": self.cities_countries,
            "job_type": self.job_type,
            "organization_short_name": self.organization_short_name,
            "organization_long_name": self.organization_long_name,
            "date_posted": self.date_posted.strftime("%Y-%m-%d %H:%M:%S"),
            "updated": self.updated.strftime("%Y-%m-%d %H:%M:%S"),
            "deadline": self.deadline.strftime("%Y-%m-%d %H:%M:%S")
            if self.deadline is not None
            else None,
            "recruitment_place": self.recruitment_place,
            "description": self.description,
            "questions_and_answers": self.questions_and_answers,
        }

    @classmethod
    def deserialize(cls, serialized_dict):
        # convert serialized dict to UNJob object
        return UNJob(
            serialized_dict["un_jobnet_id"],
            serialized_dict["title"],
            serialized_dict["department"],
            serialized_dict["grade"],
            serialized_dict["level"],
            serialized_dict["cities_countries"],
            serialized_dict["job_type"],
            serialized_dict["organization_short_name"],
            serialized_dict["organization_long_name"],
            datetime.strptime(serialized_dict["date_posted"], "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(serialized_dict["updated"], "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(serialized_dict["deadline"], "%Y-%m-%d %H:%M:%S")
            if serialized_dict["deadline"] is not None
            else None,
            serialized_dict["recruitment_place"],
            serialized_dict["description"],
            serialized_dict["questions_and_answers"],
        )
