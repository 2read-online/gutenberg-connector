"""Tests for Gutenindex parsing"""
from pytest import fixture

from app.model import Book


@fixture(name='book')
def _gutendex_book_txt():
    return {
        'id': '4',
        'media_type': 'Text',
        'copyright': False,
        'title': 'Steppenwolf',
        'formats': {
            'text/plain; charset=utf-8': 'http://url.local/4.txt',
            'image/jpeg': 'http://url.local/4.jpeg'
        },
        'authors': [{'name': 'Hermann, Hesse'}],
        'languages': ['de'],

    }


def test__parse_book_ok(book):
    """Should parse valid data
    """
    assert Book.from_gutendex(book)


def test__parse_copyright(book):
    """Should parse none if book is under copyright
    """
    book['copyright'] = True
    assert Book.from_gutendex(book) is None


def test__parse_content_type(book):
    """Should parse none if content is not text
    """
    book['media_type'] = 'non-text'
    assert Book.from_gutendex(book) is None


def test__parse_bad_format(book):
    """Should parse none if no supported format
    """
    book['formats'] = {'text/epub': 'http://url.local/3.epub', }
    assert Book.from_gutendex(book) is None
