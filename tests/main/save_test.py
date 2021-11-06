# pylint: disable=redefined-outer-name, too-many-arguments
"""Test handling /gutenberg/save endpoint"""
import gzip
import pytest
from asynctest import patch, CoroutineMock

from app.model import Book
from tests.main.conftest import get_detail


def _gutendex_book_txt():
    return {
        'results': [
            {
                'id': '3',
                'title': 'Steppenwolf',
                'formats': {
                    'text/plain; charset=utf-8': 'http://url.local/3.txt',
                    'image/jpeg': 'http://url.local/3.jpeg'
                },
                'authors': [{'name': 'Hermann, Hesse'}],
                'languages': ['de']
            }
        ]
    }


def _gutendex_book_zip():
    info = _gutendex_book_txt()
    info['results'][0]['formats']['text/plain; charset=utf-8'] = 'http://url.local/3.zip'
    return info


def _text() -> bytes:
    return b'Some text'


def _zip_text() -> bytes:
    return gzip.compress(b'Some text')


@pytest.mark.parametrize('book_info, content',
                         [(_gutendex_book_txt(), _text()), (_gutendex_book_zip(), _zip_text())])
@patch('aiohttp.ClientSession.post')
@patch('aiohttp.ClientSession.get')
def test__save_ok(mock_get, mock_post, client, headers, book_info, content):
    """Should request information from Gutendex
    then download text from Gutenberg and then save it in text storage
    """
    mock_resp = mock_get.return_value.__aenter__.return_value
    mock_resp.json = CoroutineMock(side_effect=[book_info])
    mock_resp.read = CoroutineMock(side_effect=[content])
    mock_resp.get_encoding.return_value = 'utf-8'

    mock_post.return_value.__aenter__.return_value.json = CoroutineMock(
        side_effect=[{'id': 1}])

    resp = client.post('/gutenberg/save/3?lang=en', headers=headers)

    assert resp.status_code == 200

    assert mock_get.call_args_list[0][0] == ('https://gutendex.com/books?ids=3',)
    assert mock_get.call_args_list[1][0] == (Book.from_gutendex(
        book_info['results'][0]).book_url,)

    assert mock_post.call_args_list[0][0][0] == 'http://text-storage:8000/text/create'

    post_data = mock_post.call_args_list[0][1]['json']
    assert post_data == {'author': 'Hermann, Hesse',
                         'content': 'Some text',
                         'sourceLang': 'deu',
                         'targetLang': 'eng',
                         'title': 'Steppenwolf'}


def test__save_no_jwt(client):
    """Should check access token
    """
    resp = client.post('/gutenberg/save/id?lang=de')

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
