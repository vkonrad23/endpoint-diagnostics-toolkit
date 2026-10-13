from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class Category(str, Enum):
    network = "Network"
    device = "Device Performance"
    software = "Software"
    account = "Account/Access"
    peripherals = "Peripherals"
    av = "AV/Meeting Room"
    other = "Other"


class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class Status(str, Enum):
    open = "Open"
    progress = "In Progress"
    waiting = "Waiting"
    resolved = "Resolved"
    closed = "Closed"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=5000)
    category: Category
    priority: Priority
    status: Status = Status.open
    requester_label: str | None = Field(default=None, max_length=100)


class IncidentPatch(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=3, max_length=5000)
    category: Category | None = None
    priority: Priority | None = None
    status: Status | None = None
    requester_label: str | None = Field(default=None, max_length=100)


class NoteCreate(BaseModel):
    action: str = Field(min_length=1, max_length=2000)
    result: str = Field(min_length=1, max_length=2000)
    next_step: str = Field(min_length=1, max_length=2000)


class NoteOut(NoteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime


class IncidentOut(IncidentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    notes: list[NoteOut] = []


class DeviceCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    platform: str = Field(min_length=1, max_length=60)
    owner_label: str | None = Field(default=None, max_length=100)
    status: str = Field(default="Active", max_length=30)
    notes: str = Field(default="", max_length=2000)


class DeviceOut(DeviceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    last_seen_at: datetime
