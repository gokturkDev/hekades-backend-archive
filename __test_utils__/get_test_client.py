import os
from os.path import dirname, join

import inject
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from httpx import Headers

from __test_utils__.mock_dependency_container import MockDepContainer
from business.entity.user.user_entity import UserRole
from interface.auth.auth import get_password_hash
from main.dependency_container import DepContainer
from main.main import initialize_api_instance, initialize_api_with_dependencies

load_dotenv(dotenv_path=join(dirname(__file__), ".env"))


def get_test_client_with_mock_dependencies():
    MockDepContainer.initialize_dependencies()
    inject.configure(
        lambda binder: binder.bind(DepContainer, MockDepContainer),
        once=True
    )

    api = initialize_api_instance()
    test_client = TestClient(api)
    _configure_account_for_test_client_with_mock_dependencies(test_client)
    return test_client


def get_test_client_with_dependencies() -> TestClient:
    api = initialize_api_with_dependencies()
    test_client = TestClient(api)
    _configure_account_for_test_client(test_client)
    return test_client


def _configure_account_for_test_client_with_mock_dependencies(test_client: TestClient):
    test_user_email = os.environ.get("TEST_USER_EMAIL")
    test_user_password = os.environ.get("TEST_USER_PASSWORD")

    MockDepContainer.user_repo.get.return_value.email = test_user_email
    MockDepContainer.user_repo.get.return_value.is_active = True
    MockDepContainer.user_repo.get.return_value.role = UserRole.ADMIN
    MockDepContainer.user_repo.get_user_password.return_value = get_password_hash(
        test_user_password
    )

    _configure_account_for_test_client(test_client)


def _configure_account_for_test_client(test_client: TestClient):
    test_user_email = os.environ.get("TEST_USER_EMAIL")
    test_user_password = os.environ.get("TEST_USER_PASSWORD")
    response = test_client.post(
        "/auth/login",
        data={
            "username": test_user_email,
            "password": test_user_password
        }
    )
    access_token = response.json()["access_token"]
    test_client.headers.update(Headers({"Authorization": f"Bearer {access_token}"}))
