import json
import tempfile
import unittest
from pathlib import Path

from src.fortinet_socaas.forticloud_auth import AuthClient


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

    def post(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse({
            "access_token": "access-token",
            "token_type": "Bearer",
            "refresh_token": "refresh-token",
            "expires_in": 3600,
        })


class AuthClientTests(unittest.TestCase):
    def test_get_access_token_fetches_and_persists_credentials(self):
        session = FakeSession()

        with tempfile.TemporaryDirectory() as tmpdir:
            credentials_file = Path(tmpdir) / "creds.json"
            client = AuthClient(
                api_id="api-id",
                api_password="password",
                api_client_id="client-id",
                oauth_url="https://auth.example.test/oauth/token",
                credentials_file=credentials_file,
                session=session,
            )

            token_type, access_token = client.get_access_token()
            stored = json.loads(credentials_file.read_text(encoding="utf-8"))

        self.assertEqual(token_type, "Bearer")
        self.assertEqual(access_token, "access-token")
        self.assertEqual(stored["refresh_token"], "refresh-token")
        self.assertEqual(session.calls[0]["url"], "https://auth.example.test/oauth/token")


if __name__ == "__main__":
    unittest.main()
