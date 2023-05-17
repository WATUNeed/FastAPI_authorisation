import uuid

from pydantic import BaseModel, EmailStr, validator

from utils.validation import validate_id, validate_name, validate_empty, validate_password


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


# Validation models
class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str

    @validator('name')
    def validate_name(cls, value):
        return validate_name(value)

    @validator('surname')
    def validate_surname(cls, value):
        return validate_name(value)

    @validator('password')
    def validate_password(cls, value):
        return validate_password(value)


class TaskCreate(BaseModel):
    name: str
    content: str

    @validator('name')
    def validate_name(cls, value):
        return validate_name(value)

    @validator('content')
    def validate_content(cls, value):
        return validate_empty(value)


class TaskById(BaseModel):
    task_id: uuid.UUID

    @validator('task_id')
    def validate_task_id(cls, value):
        return validate_id(value)


class TaskEdit(BaseModel):
    task_id: uuid.UUID
    name: str
    content: str

    @validator('task_id')
    def validate_task_id(cls, value):
        return validate_id(value)

    @validator('name')
    def validate_name(cls, value):
        return validate_name(value)

    @validator('content')
    def validate_content(cls, value):
        return validate_empty(value)


# Show result models
class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class ShowUserWithPassword(ShowUser):
    hashed_password: str


class ShowTask(TunedModel):
    task_id: uuid.UUID
    user_id: uuid.UUID
    name: str
    content: str


class ShowTasks(TunedModel):
    task: list[ShowTask]


class ShowToken(TunedModel):
    access_token: str


class ShowEmail(BaseModel):
    email: EmailStr


class ShowSuccess(TunedModel):
    success: bool
