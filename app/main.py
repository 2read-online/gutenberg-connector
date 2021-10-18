"""Web application"""
import logging
from typing import Optional, Dict
from urllib.parse import urlparse as url

from fastapi import FastAPI, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.requests import Request
from starlette.responses import JSONResponse
import aiohttp

from app.config import CONFIG
from app.schemas import Book

logging.basicConfig(level='DEBUG')
logger = logging.getLogger(__name__)

app = FastAPI()

SUPPORTED_FORMATS = ["text/plain", "text/plain;charset=utf-8"]


@AuthJWT.load_config
def get_config():
    """Load settings
    """
    return CONFIG


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_request: Request, exc: AuthJWTException):
    """
    JWT exception
    :param _request:
    :param exc:
    :return:
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


def _find_supported_format(formats: Dict[str, str]) -> Optional[str]:
    for mime_type, link in formats.items():
        if mime_type.strip().replace(' ', '').lower() in SUPPORTED_FORMATS:
            return link

    return None


def _substitute_domain(link):
    return CONFIG.gutenberg_url + url(link).path


@app.get('/gutenberg/search')
async def search(q: str, authorize: AuthJWT = Depends()):
    """Search texts in Gutendex
    """
    authorize.jwt_required()

    search_url = f'{CONFIG.gutendex_url}/books?search={q}'
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as resp:
            data = await resp.json()
            logger.info(data)

            books = []
            for book in data['results']:
                formats_ = book['formats']
                download_link = _find_supported_format(formats_)

                if download_link:
                    download_link = _substitute_domain(download_link)
                    cover_link = None
                    if 'image/jpeg' in formats_:
                        cover_link = _substitute_domain(formats_['image/jpeg'])

                    author = book['authors'][0]['name'] if len(book['authors']) > 0 else 'unknown'
                    books.append(Book(id=book['id'], title=book['title'],
                                      language=book['languages'][0],
                                      author=author,
                                      bookUrl=download_link,
                                      coverUrl=cover_link))

    return books
