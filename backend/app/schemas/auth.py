"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    """Schema for registering a new user."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="teacher", min_length=1, max_length=20)


class UserLogin(BaseModel):
    """Schema for logging in an existing user."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """Schema for returning an access token."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for returning a user summary."""

    id: int
    name: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)
