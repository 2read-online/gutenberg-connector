"""Configuration"""
from pydantic import BaseSettings, Field, HttpUrl, AnyHttpUrl


class Config(BaseSettings):
    """App configuration"""
    gutendex_url: HttpUrl = Field("https://gutendex.com")
    gutenberg_url: HttpUrl = Field("https://gutenberg.org")
    text_storage_url: AnyHttpUrl = Field('http://nginx:8080')
    authjwt_secret_key: str = Field(description='Secret key for JWT',
                                    env='secret_key', default='secret')

CONFIG = Config()
