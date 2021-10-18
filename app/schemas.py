"""Schemas for HTTP data"""
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Book(BaseModel):
    """Book from Gutendex"""
    id: str = Field(description='ID of book on Gutenberg')
    title: str = Field(description='Title')
    language: str = Field(description='Language')
    author: str = Field(description='Author')
    book_url: HttpUrl = Field(description='URL to download book', alias='bookUrl')
    cover_url: Optional[HttpUrl] = Field(description='URL to download cover', alias='coverUrl')
