# pylint: disable=redefined-outer-name, too-many-arguments
"""Test handling /gutenberg/search endpoint
"""
import pytest
from asynctest import patch, CoroutineMock

from tests.main.conftest import get_detail


@pytest.fixture(name='response_ok')
def _fixture_response_ok():
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
                'languages': ['de'],
                'copyright': False,
                'media_type': 'Text',
            },
            {
                'id': '2',
                'title': 'Steppenwolf',
                'formats': {'text/plain': 'http://url.local/2.txt'},
                'authors': [{'name': 'Hermann, Hesse'}],
                'languages': ['en'],
                'copyright': False,
                'media_type': 'Text',
            }
        ]
    }


@pytest.fixture(name='response_unsupported_format')
def _fixture_unsupported_format(response_ok):
    response_ok['results'][1]['formats'] = {'text/epub': 'http://url.local/2.epub'}
    return response_ok


@pytest.fixture(name='response_unknown_author')
def _fixture_response_unknown_author(response_ok):
    response_ok['results'][0]['authors'] = []
    return response_ok


@patch('aiohttp.ClientSession.get')
def test__search_ok(mock_get, client, headers, response_ok):
    """Should parse a valid response
    """
    mock_get.return_value.__aenter__.return_value.json = CoroutineMock(side_effect=[response_ok])

    resp = client.get('/gutenberg/search?q=Hesse', headers=headers)
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == 2
    assert data[0]['id'] == '1'
    assert data[0]['title'] == 'Maerechen'
    assert data[0]['language'] == 'de'
    assert data[0]['author'] == 'Hermann, Hesse'
    assert data[0]['bookUrl'] == 'https://gutenberg.org/1.txt'
    assert data[0]['coverUrl'] == 'https://gutenberg.org/1.jpeg'

    assert data[1]['id'] == '2'
    assert data[1]['title'] == 'Steppenwolf'
    assert data[1]['language'] == 'en'
    assert data[1]['author'] == 'Hermann, Hesse'
    assert data[1]['bookUrl'] == 'https://gutenberg.org/2.txt'
    assert data[1]['coverUrl'] is None


@patch('aiohttp.ClientSession.get')
def test__search_unsupported_format(mock_get, client, headers, response_unsupported_format):
    """Should skip unsupported format
    """
    mock_get.return_value.__aenter__.return_value.json = CoroutineMock(
        side_effect=[response_unsupported_format])

    resp = client.get('/gutenberg/search?q=Hesse', headers=headers)
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == 1
    assert data[0]['id'] == '1'


@patch('aiohttp.ClientSession.get')
def test__search_unknown_author(mock_get, client, headers, response_unknown_author):
    """Should set author as unknown if no data in response
    """
    mock_get.return_value.__aenter__.return_value.json = CoroutineMock(
        side_effect=[response_unknown_author])

    resp = client.get('/gutenberg/search?q=Hesse', headers=headers)
    assert resp.status_code == 200

    data = resp.json()
    assert len(data) == 2
    assert data[0]['author'] == 'unknown'


def test__search_no_jwt(client):
    """Should check access token
    """
    resp = client.get('/gutenberg/search?q=Hesse')

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
