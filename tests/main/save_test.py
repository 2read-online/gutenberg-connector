# pylint: disable=redefined-outer-name, too-many-arguments
"""Test handling /gutenberg/save endpoint"""
import pytest
from asynctest import patch, CoroutineMock

from app.model import Book
from tests.main.conftest import get_detail


@pytest.fixture(name='gutendex_response_ok')
def _gutendex_response_ok():
    return {
        'results': [
            {
                'id': '1',
                'title': 'Maerechen',
                'formats': {
                    'text/plain; charset=utf-8': 'http://url.local/1.txt',
                    'image/jpeg': 'http://url.local/1.jpeg'
                },
                'authors': [{'name': 'Hermann, Hesse'}],
                'languages': ['de']
            }
        ]
    }


@pytest.fixture(name='text')
def _text():
    return 'Some text'


@patch('aiohttp.ClientSession.post')
@patch('aiohttp.ClientSession.get')
def test__save_ok(mock_get, mock_post, client, headers, gutendex_response_ok, text):
    """Should request information from Gutendex then download text from Gutenberg and then save it in text storage
    """
    mock_get.return_value.__aenter__.return_value.json = CoroutineMock(side_effect=[gutendex_response_ok])
    mock_get.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=[text])
    mock_post.return_value.__aenter__.return_value.json = CoroutineMock(side_effect=[{'id': 1}])

    resp = client.post('/gutenberg/save/1?lang=en', headers=headers)

    assert resp.status_code == 200

    assert mock_get.call_args_list[0][0] == ('https://gutendex.com/books?ids=1',)
    assert mock_get.call_args_list[1][0] == (Book.from_gutendex(gutendex_response_ok['results'][0]).book_url,)

    assert mock_post.call_args_list[0][0][0] == 'http://text-storage:8000/text/create'

    post_data = mock_post.call_args_list[0][1]['json']
    assert post_data == {'author': 'Hermann, Hesse',
                         'content': 'Some text',
                         'sourceLang': 'deu',
                         'targetLang': 'eng',
                         'title': 'Maerechen'}


def test__save_no_jwt(client):
    """Should check access token
    """
    resp = client.post('/gutenberg/save/id?lang=de')

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
