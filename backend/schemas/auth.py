from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=80, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)
    full_name: str = Field(default="", max_length=160)


class LoginIn(BaseModel):
    username: str = Field(min_length=2, max_length=160)  # accepts username or email
    password: str = Field(min_length=1, max_length=200)
