"""Configuration"""
from pydantic import BaseSettings, Field, HttpUrl, AnyHttpUrl


class Config(BaseSettings):
    """App configuration"""
    log_level: str = Field('INFO')
    gutendex_url: HttpUrl = Field("https://gutendex.com")
    gutenberg_url: HttpUrl = Field("https://gutenberg.org")
    text_storage_url: AnyHttpUrl = Field('http://text-storage:8000')
    authjwt_secret_key: str = Field(description='Secret key for JWT',
                                    env='secret_key', default='secret')

CONFIG = Config()
