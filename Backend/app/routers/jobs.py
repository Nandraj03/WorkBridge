from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.constants import Role
from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobOut, JobUpdate
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])
employer_only = require_role(Role.EMPLOYER)


@router.post("", response_model=JobOut, status_code=201)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    employer: User = Depends(employer_only),
):
    return job_service.create_job(db, employer, data)


@router.get("/mine", response_model=list[JobOut])
def my_jobs(
    status: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    employer: User = Depends(employer_only),
):
    return job_service.list_my_jobs(db, employer, status, limit, offset)


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return job_service.get_job_for_viewer(db, job_id, user)


@router.put("/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    data: JobUpdate,
    db: Session = Depends(get_db),
    employer: User = Depends(employer_only),
):
    return job_service.update_job(db, employer, job_id, data)


@router.post("/{job_id}/publish", response_model=JobOut)
def publish_job(
    job_id: int,
    db: Session = Depends(get_db),
    employer: User = Depends(employer_only),
):
    return job_service.publish_job(db, employer, job_id)


@router.post("/{job_id}/close", response_model=JobOut)
def close_job(
    job_id: int,
    db: Session = Depends(get_db),
    employer: User = Depends(employer_only),
):
    return job_service.close_job(db, employer, job_id)


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    employer: User = Depends(employer_only),
):
    job_service.delete_job(db, employer, job_id)
    return Response(status_code=204)