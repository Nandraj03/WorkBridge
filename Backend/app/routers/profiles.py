from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import Role, VerificationStatus
from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import EmployerProfile, User, WorkerProfile
from app.schemas.profile import (EmployerProfileOut, EmployerProfileUpdate,
                                 VerificationSubmit, WorkerProfileOut,
                                 WorkerProfileUpdate)

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _get_worker_profile(db: Session, user: User) -> WorkerProfile:
    profile = db.scalar(select(WorkerProfile).where(WorkerProfile.user_id == user.id))
    if not profile:  # create lazily if somehow missing
        profile = WorkerProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _get_employer_profile(db: Session, user: User) -> EmployerProfile:
    profile = db.scalar(select(EmployerProfile).where(EmployerProfile.user_id == user.id))
    if not profile:
        profile = EmployerProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


# ---------- Worker ----------
@router.get("/worker/me", response_model=WorkerProfileOut)
def get_worker_profile(
    user: User = Depends(require_role(Role.WORKER)), db: Session = Depends(get_db)
):
    return _get_worker_profile(db, user)


@router.put("/worker/me", response_model=WorkerProfileOut)
def update_worker_profile(
    data: WorkerProfileUpdate,
    user: User = Depends(require_role(Role.WORKER)),
    db: Session = Depends(get_db),
):
    profile = _get_worker_profile(db, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


# ---------- Employer ----------
@router.get("/employer/me", response_model=EmployerProfileOut)
def get_employer_profile(
    user: User = Depends(require_role(Role.EMPLOYER)), db: Session = Depends(get_db)
):
    return _get_employer_profile(db, user)


@router.put("/employer/me", response_model=EmployerProfileOut)
def update_employer_profile(
    data: EmployerProfileUpdate,
    user: User = Depends(require_role(Role.EMPLOYER)),
    db: Session = Depends(get_db),
):
    profile = _get_employer_profile(db, user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/employer/verification", response_model=EmployerProfileOut)
def submit_verification(
    data: VerificationSubmit,
    user: User = Depends(require_role(Role.EMPLOYER)),
    db: Session = Depends(get_db),
):
    profile = _get_employer_profile(db, user)
    if profile.verification_status == VerificationStatus.APPROVED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Your account is already verified")
    if not profile.business_name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add your business name to your profile first")
    profile.verification_details = data.verification_details
    profile.verification_status = VerificationStatus.PENDING  # also resets a rejected one
    db.commit()
    db.refresh(profile)
    return profile