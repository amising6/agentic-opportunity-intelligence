"""Configurable multi-source opportunity discovery."""

import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .adapters.public_jobs import (
    greenhouse, lever, filter_jobs
)

ADAPTERS = {
    "greenhouse": greenhouse,
    "lever": lever,
}


def load_sources(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def discover(sources, keyword="", location=""):

    def process(source):
        try:
            adapter = ADAPTERS[source["provider"]]

            jobs = adapter(
                source["board"],
                source["organization"]
            )

            matches = filter_jobs(
                jobs, keyword, location
            )

            return matches, {
                "organization": source["organization"],
                "provider": source["provider"],
                "total": len(jobs),
                "matched": len(matches),
                "status": "success",
            }

        except Exception as exc:
            return [], {
                "organization": source["organization"],
                "provider": source["provider"],
                "total": 0,
                "matched": 0,
                "status": "failed",
                "error": str(exc),
            }

    active = [
        source for source in sources
        if source.get("enabled", True)
    ]

    unique = {}
    reports = []

    with ThreadPoolExecutor(max_workers=4) as pool:
        for jobs, report in pool.map(process, active):
            reports.append(report)

            for job in jobs:
                unique[job.id] = job

    return list(unique.values()), reports
