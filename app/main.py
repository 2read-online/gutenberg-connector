"""Web application"""
import gzip
import logging
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.requests import Request
from starlette.responses import JSONResponse
import aiohttp

from app.config import CONFIG
from app.model import Book, LANG_CODE_MAP

logging.basicConfig(level=CONFIG.log_level)
logger = logging.getLogger(__name__)

app = FastAPI()


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


@app.get('/gutenberg/search')
async def search(q: str, authorize: AuthJWT = Depends()):
    """Search texts in Gutendex
    """
    authorize.jwt_required()

    search_url = f'{CONFIG.gutendex_url}/books?search={q}'
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as resp:
            data = await resp.json()

            books: List[Book] = []
            for result in data['results']:
                book = Book.from_gutendex(result)
                if book:
                    books.append(book)

            logger.info('Found %d books for query: %s', len(books), q)
            return books


@app.post('/gutenberg/save/{book_id}')
async def save(book_id: str, lang: str,
               authorize: AuthJWT = Depends(), authorization: str = Header(None)):
    """Download a book and save it in text storage
    """
    authorize.jwt_required()

    search_url = f'{CONFIG.gutendex_url}/books?ids={book_id}'

    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as resp:
            data = await resp.json()
            book = Book.from_gutendex(data['results'][0])
            logger.debug('Save book: %s', str(book))

        async with session.get(book.book_url) as resp:
            is_zip = book.book_url.path.split('.')[-1] == 'zip'
            data: bytes = await resp.read()
            if is_zip:
                data = gzip.decompress(data)

            content = data.decode(resp.get_encoding())

        new_text = {
            'title': book.title,
            'author': book.author,
            'sourceLang': LANG_CODE_MAP[book.language],
            'targetLang': LANG_CODE_MAP[lang],
            'content': content
        }

        async with session.post(CONFIG.text_storage_url + '/text/create', json=new_text,
                                headers={'Authorization': authorization}) as resp:
            data = await resp.json()
            if not resp.ok:
                logger.error('Failed save book: %s', data)
                raise HTTPException(status_code=resp.status, detail=data['detail'])

            return data
