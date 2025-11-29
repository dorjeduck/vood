"""Export job management for development server."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Callable

from vood.core.logger import get_logger

logger = get_logger()


class ExportStatus(Enum):
    """Status of an export job"""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


class ExportFormat(Enum):
    """Supported export formats"""

    MP4 = "mp4"
    GIF = "gif"
    HTML = "html"


@dataclass
class ExportJob:
    """Represents an export job"""

    job_id: str
    format: ExportFormat
    status: ExportStatus = ExportStatus.QUEUED
    progress: float = 0.0  # 0.0 to 1.0
    message: str = ""
    output_file: Optional[Path] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "format": self.format.value,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "output_file": str(self.output_file) if self.output_file else None,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class ExportJobManager:
    """Manages export jobs for the development server"""

    def __init__(self, output_dir: Path):
        """
        Initialize export job manager.

        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.jobs: Dict[str, ExportJob] = {}

    def create_job(self, format: ExportFormat) -> ExportJob:
        """
        Create a new export job.

        Args:
            format: Export format

        Returns:
            Created ExportJob
        """
        job_id = str(uuid.uuid4())[:8]
        job = ExportJob(job_id=job_id, format=format)
        self.jobs[job_id] = job
        logger.info(f"Created export job {job_id} for format {format.value}")
        return job

    def get_job(self, job_id: str) -> Optional[ExportJob]:
        """
        Get job by ID.

        Args:
            job_id: Job ID

        Returns:
            ExportJob or None if not found
        """
        return self.jobs.get(job_id)

    def update_job(
        self,
        job_id: str,
        status: Optional[ExportStatus] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        output_file: Optional[Path] = None,
        error: Optional[str] = None,
    ):
        """
        Update job status.

        Args:
            job_id: Job ID
            status: New status
            progress: Progress (0.0 to 1.0)
            message: Status message
            output_file: Output file path
            error: Error message
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            return

        if status is not None:
            job.status = status
        if progress is not None:
            job.progress = progress
        if message is not None:
            job.message = message
        if output_file is not None:
            job.output_file = output_file
        if error is not None:
            job.error = error
            job.status = ExportStatus.ERROR

        if status == ExportStatus.COMPLETE:
            job.completed_at = datetime.now()
            job.progress = 1.0

        logger.debug(f"Updated job {job_id}: {job.status.value} ({job.progress:.0%})")

    async def run_export_job(
        self,
        job_id: str,
        export_func: Callable,
        *args,
        **kwargs,
    ):
        """
        Run an export job in the background.

        Args:
            job_id: Job ID
            export_func: Export function to call
            *args: Arguments for export function
            **kwargs: Keyword arguments for export function
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        try:
            self.update_job(job_id, status=ExportStatus.PROCESSING, message="Starting export...")

            # Run export function in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            output_file = await loop.run_in_executor(None, export_func, *args, **kwargs)

            self.update_job(
                job_id,
                status=ExportStatus.COMPLETE,
                message="Export complete",
                output_file=Path(output_file),
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Export job {job_id} failed: {error_msg}")
            self.update_job(
                job_id,
                status=ExportStatus.ERROR,
                error=error_msg,
                message="Export failed",
            )

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running export job.

        Args:
            job_id: Job ID

        Returns:
            True if job was cancelled, False if not found or already complete
        """
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status in (ExportStatus.COMPLETE, ExportStatus.ERROR, ExportStatus.CANCELLED):
            return False

        job.status = ExportStatus.CANCELLED
        job.message = "Cancelled by user"
        job.completed_at = datetime.now()
        logger.info(f"Cancelled job {job_id}")
        return True

    def cleanup_old_jobs(self, max_age_seconds: int = 3600):
        """
        Remove old completed/error jobs.

        Args:
            max_age_seconds: Maximum age for completed jobs (default: 1 hour)
        """
        now = datetime.now()
        to_remove = []

        for job_id, job in self.jobs.items():
            if job.status in (ExportStatus.COMPLETE, ExportStatus.ERROR, ExportStatus.CANCELLED):
                age = (now - job.created_at).total_seconds()
                if age > max_age_seconds:
                    to_remove.append(job_id)

        for job_id in to_remove:
            del self.jobs[job_id]
            logger.debug(f"Removed old job {job_id}")
