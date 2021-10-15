from pydantic import BaseModel, Field


class Book(BaseModel):
    id: int = Field(description="ID of book on Gutenberg")
    title: str = Field(description="Title")
    language: str = Field(description="Language")
