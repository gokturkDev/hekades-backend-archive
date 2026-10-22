from __test_utils__.get_test_client import get_test_client_with_mock_dependencies
from __test_utils__.mock_dependency_container import MockDepContainer


class TestRouter:
    @classmethod
    def setup_class(cls):
        cls.client = get_test_client_with_mock_dependencies()

    def setup_method(self):
        MockDepContainer.reset_mocks()
