from pydantic import BaseModel, Field


# SCHEMA AUTENTICAÇÃO
class Token(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class FilterPage(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=10, le=100)
