import json
import tempfile
import unittest
from pathlib import Path

from src.fortinet_socaas.fortinet_client import FortinetClient
from src.utils.models import Config


class FakeResponse:
    def __init__(self, payload: dict):
        self.status_code = 200
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse({"result": {"data": [{"uuid": "alert-1"}]}})


class FortinetClientTests(unittest.TestCase):
    def test_send_request_adds_alert_date_params(self):
        session = FakeSession()

        with tempfile.TemporaryDirectory() as tmpdir:
            credentials_file = Path(tmpdir) / "creds.json"
            credentials_file.write_text(json.dumps({
                "access_token": "access-token",
                "token_type": "Bearer",
                "refresh_token": "refresh-token",
                "expires_at": "2099-01-01T00:00:00Z",
            }), encoding="utf-8")

            client = FortinetClient(
                socaas_config=Config(
                    url="https://socaas.example.test",
                    api_id="api-id",
                    password="password",
                    client_id="client-id",
                ),
                oauth_url="https://auth.example.test/oauth/token",
                credentials_file=credentials_file,
                session=session,
            )

            response = client.send_request(
                http_method="GET",
                http_resource="/alert",
                date_from="2026-07-05T11:55:00Z",
                date_to="2026-07-05T12:00:00Z",
            )

        self.assertEqual(response["result"]["data"][0]["uuid"], "alert-1")
        self.assertEqual(session.calls[0]["url"], "https://socaas.example.test/socaasAPI/v1/alert")
        self.assertEqual(session.calls[0]["params"]["created_date_from"], "2026-07-05T11:55:00Z")
        self.assertEqual(session.calls[0]["params"]["created_date_to"], "2026-07-05T12:00:00Z")


if __name__ == "__main__":
    unittest.main()
