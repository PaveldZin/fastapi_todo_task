from pydantic import BaseModel, Field, ConfigDict

class Task(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    model_config = ConfigDict(
        extra="forbid",
    )