from __test_utils__.mock_dependency_container import MockDepContainer
from __test_utils__.mock_utils import stream_string
from __unittests__.interface.routers.test_router import TestRouter


class TestSummarizeResource(TestRouter):
    def test_summarize_resource(self):
        MockDepContainer.resource_summarizer.summarize_resource.return_value = \
            stream_string("Test summary")

        response = self.client.post("/resource/summarize", files={"resource_file": ("test.jpg", b"test")})

        assert response.status_code == 200

        response_packets = []

        for packet in response.iter_lines():
            response_packets.append(packet)

        msg = ""
        for packet in response_packets:
            msg += packet
        assert msg == "Test summary"
        MockDepContainer.resource_summarizer.summarize_resource.assert_called_once()
