"""Configuration"""
from pydantic import BaseSettings, Field, HttpUrl


class Config(BaseSettings):
    """App configuration"""
    gutendex_url: HttpUrl = Field("https://gutendex.com")
    gutenberg_url: HttpUrl = Field("https://gutenberg.org")


CONFIG = Config()
