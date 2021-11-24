"""Schemas for HTTP data"""
import logging
from typing import Optional, Dict
from urllib.parse import urlparse as url

from pydantic import BaseModel, Field, HttpUrl

from app.config import CONFIG

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = ["text/plain", "text/plain;charset=utf-8"]

LANG_CODE_MAP = {
    'bg': 'bul',
    'cs': 'ces',
    'da': 'dan',
    'de': 'deu',
    'el': 'ell',
    'en': 'eng',
    'es': 'spa',
    'et': 'est',
    'fi': 'fin',
    'fr': 'fra',
    'hu': 'hun',
    'it': 'ita',
    'js': 'jpn',
    'lt': 'lit',
    'lv': 'lav',
    'nl': 'nld',
    'pl': 'pol',
    'pt': 'por',
    'ro': 'ron',
    'ru': 'rus',
    'sk': 'slk',
    'sl': 'slv',
    'sv': 'swe',
    'zh': 'zho',
}


def _find_supported_format(formats: Dict[str, str]) -> Optional[str]:
    for mime_type, link in formats.items():
        if mime_type.strip().replace(' ', '').lower() in SUPPORTED_FORMATS:
            return link

    return None


def _substitute_domain(link):
    return CONFIG.gutenberg_url + url(link).path


class Book(BaseModel):
    """Book from Gutendex"""
    id: str = Field(description='ID of book on Gutenberg')
    title: str = Field(description='Title')
    language: str = Field(description='Language')
    author: str = Field(description='Author')
    book_url: HttpUrl = Field(description='URL to download book', alias='bookUrl')
    cover_url: Optional[HttpUrl] = Field(description='URL to download cover', alias='coverUrl')

    @classmethod
    def from_gutendex(cls, data: dict):
        """Parse Gutendex output
        """
        if data['media_type'].strip().lower() != 'text' or data['copyright']:
            logger.debug('Bad content for %s', data)
            return None

        formats_ = data['formats']
        download_link = _find_supported_format(formats_)

        if not download_link:
            logger.debug('No supported format for %s', data)
            return None

        download_link = _substitute_domain(download_link)
        cover_link = None
        if 'image/jpeg' in formats_:
            cover_link = _substitute_domain(formats_['image/jpeg'])

        author = data['authors'][0]['name'] if len(data['authors']) > 0 else 'unknown'

        return cls(id=data['id'], title=data['title'],
                   language=data['languages'][0],
                   author=author,
                   bookUrl=download_link,
                   coverUrl=cover_link)
