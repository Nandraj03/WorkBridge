from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import (AwareDatetime, BaseModel, ConfigDict, Field,
                      model_validator)


class JobCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10)
    category: str = Field(min_length=2, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=80)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    workers_needed: int = Field(ge=1, le=500)
    wage: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    wage_type: Literal["fixed", "hourly"] = "fixed"
    payment_terms: str | None = None
    start_time: AwareDatetime  # must include a timezone, e.g. 2026-10-25T09:00:00+05:30
    end_time: AwareDatetime

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=10)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=80)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    workers_needed: int | None = Field(default=None, ge=1, le=500)
    wage: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    wage_type: Literal["fixed", "hourly"] | None = None
    payment_terms: str | None = None
    start_time: AwareDatetime | None = None
    end_time: AwareDatetime | None = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employer_id: int
    title: str
    description: str
    category: str
    address: str | None
    city: str | None
    lat: float | None
    lng: float | None
    workers_needed: int
    workers_selected: int
    wage: Decimal
    wage_type: str
    payment_terms: str | None
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime