from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import JobStatus, Role, VerificationStatus
from app.models.job import Job
from app.models.user import EmployerProfile, User
from app.schemas.job import JobCreate, JobUpdate


def _get_owned_job(db: Session, job_id: int, employer: User) -> Job:
    job = db.get(Job, job_id)
    # 404 (not 403) so we don't reveal that someone else's job exists
    if not job or job.employer_id != employer.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job


def _require_verified(db: Session, employer: User) -> None:
    profile = db.scalar(select(EmployerProfile).where(EmployerProfile.user_id == employer.id))
    if not profile or profile.verification_status != VerificationStatus.APPROVED:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Your employer account must be verified before you can publish jobs",
        )


def create_job(db: Session, employer: User, data: JobCreate) -> Job:
    job = Job(employer_id=employer.id, status=JobStatus.DRAFT, **data.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_my_jobs(db: Session, employer: User, status_filter: str | None, limit: int, offset: int):
    stmt = select(Job).where(Job.employer_id == employer.id)
    if status_filter:
        stmt = stmt.where(Job.status == status_filter)
    stmt = stmt.order_by(Job.created_at.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()


def get_job_for_viewer(db: Session, job_id: int, user: User) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    can_see = (
        job.employer_id == user.id
        or user.role == Role.ADMIN
        or job.status in (JobStatus.OPEN, JobStatus.FILLED)
    )
    if not can_see:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job


def update_job(db: Session, employer: User, job_id: int, data: JobUpdate) -> Job:
    job = _get_owned_job(db, job_id, employer)
    if job.status not in (JobStatus.DRAFT, JobStatus.OPEN):
        raise HTTPException(status.HTTP_409_CONFLICT, "Only draft or open jobs can be edited")
    if job.workers_selected > 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cannot edit a job after workers are selected")

    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(job, field, value)

    if job.end_time <= job.start_time:
        db.rollback()
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "end_time must be after start_time")

    db.commit()
    db.refresh(job)
    return job


def publish_job(db: Session, employer: User, job_id: int) -> Job:
    job = _get_owned_job(db, job_id, employer)
    if job.status != JobStatus.DRAFT:
        raise HTTPException(status.HTTP_409_CONFLICT, "Only draft jobs can be published")
    _require_verified(db, employer)
    if job.start_time <= datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "start_time must be in the future")
    job.status = JobStatus.OPEN
    db.commit()
    db.refresh(job)
    return job


def close_job(db: Session, employer: User, job_id: int) -> Job:
    job = _get_owned_job(db, job_id, employer)
    if job.status != JobStatus.OPEN:
        raise HTTPException(status.HTTP_409_CONFLICT, "Only open jobs can be closed")
    job.status = JobStatus.CLOSED
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, employer: User, job_id: int) -> None:
    job = _get_owned_job(db, job_id, employer)
    if job.status != JobStatus.DRAFT:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Only draft jobs can be deleted. Close published jobs instead.",
        )
    db.delete(job)
    db.commit()