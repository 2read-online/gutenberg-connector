# pylint: disable=redefined-outer-name, too-many-arguments
"""Test handling Translate Request"""
from tests.main.conftest import get_detail


def test__search_no_jwt(client):
    """Should check access token"""
    resp = client.get('/gutenberg/search?q=Hesse')

    assert resp.status_code == 401
    assert get_detail(resp.content) == "Missing Authorization Header"
