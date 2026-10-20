from pydantic import BaseModel, ConfigDict, Field


class WorkerProfileUpdate(BaseModel):
    skills: str | None = Field(default=None, max_length=1000)
    experience: str | None = Field(default=None, max_length=2000)
    availability: str | None = Field(default=None, max_length=255)
    preferred_categories: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=80)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)


class WorkerProfileOut(WorkerProfileUpdate):
    model_config = ConfigDict(from_attributes=True)
    user_id: int


class EmployerProfileUpdate(BaseModel):
    business_name: str | None = Field(default=None, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=80)


class EmployerProfileOut(EmployerProfileUpdate):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    verification_details: str | None = None
    verification_status: str


class VerificationSubmit(BaseModel):
    verification_details: str = Field(min_length=10, max_length=2000)