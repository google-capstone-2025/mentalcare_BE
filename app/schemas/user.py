from pydantic import BaseModel, HttpUrl

class UserClaims(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    picture: HttpUrl | None = None
