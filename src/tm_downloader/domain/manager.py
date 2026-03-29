from __future__ import annotations

import uuid
from typing import Dict

from telethon import TelegramClient

from tm_downloader.domain.model import DownloadState, DownloadJob


class DownloadManager:

    def __init__(self, client: TelegramClient, event=None):
        self.client = client
        self.jobs: Dict[str, DownloadJob] = {}
        self.event = event
        self.NUM_CONSUMERS = 3

    def change_job_state(self, id_job: str, state: DownloadState):
        download_job = self.jobs[id_job]
        assert download_job is not None, "Job not found."
        download_job.transition(new_state=state)


    def crete_job(self, url: str) -> DownloadJob:
        job = DownloadJob(url, str(uuid.uuid4()))
        self.jobs[job.id_job:job] = job

        return job

    def delete_job(self, id_job: str) -> DownloadJob:
        return self.jobs.pop(id_job)

    def resume_job(self, id_job: str) -> DownloadJob | None:
        if self.can_activate_job(id_job):
            return self.jobs[id_job]
        return None

    def can_activate_job(self, id_job: str) -> bool:
        if self.jobs.get(id_job).error:
            return False
        return True
