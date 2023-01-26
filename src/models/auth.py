from pydantic import BaseModel, Field


class UserAuthModel(BaseModel):
    email: str

class InUserAuthModel(BaseModel):
    email: str = Field(
        regex=r"\A[\w\-\.]+@([\w-]+\.)+[\w-]{2,4}\Z", 
        example="example@example.com"
    )
    password: str