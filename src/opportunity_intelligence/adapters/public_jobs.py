"""Read-only discovery from public ATS job boards."""

import json
import re
from urllib.request import Request, urlopen
from urllib.parse import quote
from html import unescape

from ..core import Opportunity


SKILLS = (
    "Python", "SQL", "Spark", "Databricks",
    "Snowflake", "AWS", "Azure", "GCP",
    "Kafka", "Airflow", "dbt", "Terraform",
    "Kubernetes", "Docker", "Java", "Scala",
    "PostgreSQL", "Machine Learning", "ETL",
    "Data Modeling", "APIs", "Git"
)


def fetch_json(url):
    request = Request(
        url,
        headers={
            "User-Agent": "OpportunityIntelligence/1.1",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def clean_text(value):
    return re.sub(
        r"<[^>]+>", " ", unescape(value or "")
    )


def extract_skills(description):
    text = clean_text(description)
    return tuple(
        skill for skill in SKILLS
        if re.search(
            r"(?<!\w)" + re.escape(skill) + r"(?!\w)",
            text,
            re.IGNORECASE,
        )
    )


def greenhouse(board, organization=None):
    board = board.strip().lower()

    if not board:
        raise ValueError("Board identifier is required")

    url = (
        "https://boards-api.greenhouse.io/v1/boards/"
        + quote(board, safe="")
        + "/jobs?content=true"
    )

    payload = fetch_json(url)

    return [
        Opportunity(
            id=f"greenhouse:{board}:{job['id']}",
            title=job["title"],
            organization=organization or board,
            required_skills=extract_skills(
                job.get("content", "")
            ),
            salary_max=None,
            location=(
                job.get("location", {}).get("name")
                or "unknown"
            ),
            source_url=job.get("absolute_url", ""),
            description=clean_text(
                job.get("content", "")
            ),
        )
        for job in payload.get("jobs", [])
    ]


def lever(board, organization=None):
    board = board.strip().lower()

    if not board:
        raise ValueError("Board identifier is required")

    url = (
        "https://api.lever.co/v0/postings/"
        + quote(board, safe="")
        + "?mode=json"
    )

    payload = fetch_json(url)

    return [
        Opportunity(
            id=f"lever:{board}:{job['id']}",
            title=job["text"],
            organization=organization or board,
            required_skills=extract_skills(
                " ".join([
                    job.get("descriptionPlain") or "",
                    job.get("description") or "",
                    job.get("additionalPlain") or "",
                    " ".join(
                        item.get("content") or ""
                        for item in job.get("lists", [])
                    ),
                ])
            ),
            salary_max=None,
            location=(
                job.get("categories", {}).get("location")
                or "unknown"
            ),
            source_url=job.get("hostedUrl", ""),
            description=clean_text(" ".join([
                job.get("descriptionPlain")
                or job.get("description") or "",
                " ".join(
                    (item.get("text") or "") + " " +
                    (item.get("content") or "")
                    for item in job.get("lists", [])
                ),
                job.get("additionalPlain")
                or job.get("additional") or "",
            ])),
        )
        for job in payload
    ]



def filter_jobs(jobs, keyword="", location=""):
    """Match title concepts without requiring exact phrases."""

    def normalize(value):
        words = re.findall(r"[a-z0-9]+", value.casefold())

        aliases = {
            "engineering": "engineer",
            "engineers": "engineer",
            "engineered": "engineer",
            "platforms": "platform",
            "developers": "developer",
            "architects": "architect",
        }

        return {
            aliases.get(word, word)
            for word in words
            if word not in {
                "a", "an", "the", "and",
                "of", "for", "in", "jobs",
                "roles", "positions"
            }
        }

    required = normalize(keyword)
    location = location.casefold().strip()

    return [
        job for job in jobs
        if required.issubset(normalize(job.title))
        and (
            not location
            or location in job.location.casefold()
        )
    ]
