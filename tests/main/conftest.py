# pylint: skip-file
import json
import pytest
from fastapi_jwt_auth import AuthJWT
from starlette.testclient import TestClient
from typing import Dict


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def user_id() -> str:
    return '60c0b2d700569d97f8a93dcd'


@pytest.fixture
def token(user_id: str) -> str:
    auth = AuthJWT()
    return auth.create_access_token(subject=str(user_id))


@pytest.fixture
def headers(token: str) -> Dict[str, str]:
    return {'Authorization': f'Bearer {token}'}


def get_detail(content: str) -> str:
    return json.loads(content)['detail']
