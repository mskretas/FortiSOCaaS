import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from requests import Session


DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class AuthClient:

    def __init__(
        self,
        api_id: str,
        api_password: str,
        api_client_id: str,
        oauth_url: str,
        credentials_file: Path,
        session: Session | None = None,
    ) -> None:
        self._api_id = api_id
        self._api_password = api_password
        self._api_client_id = api_client_id
        self._oauth_url = oauth_url
        self._credentials_file = credentials_file
        self._session = session or Session()

        try:
            with self._credentials_file.open("r", encoding="utf-8") as f:
                run_vars = json.loads(f.read())
                self.access_token = run_vars["access_token"]
                self.token_type = run_vars["token_type"]
                self.refresh_token = run_vars["refresh_token"]
                self._expires_at = run_vars["expires_at"]
        except FileNotFoundError:
            self.access_token = None
            self.token_type = None
            self.refresh_token = None
            self._expires_at = None

    def __get_oauth_access_token(self, grant_type: str) -> None:
        oauth_headers = {
            "Content-Type": "application/json"
        }

        if grant_type == "password":
            oauth_body = {
                "username": self._api_id,
                "password": self._api_password,
                "client_id": self._api_client_id,
                "grant_type": f"{grant_type}"
            }
        elif grant_type == "refresh_token":
            oauth_body = {
                "client_id": self._api_client_id,
                "refresh_token": self.refresh_token,
                "grant_type": f"{grant_type}"
            }
        else:
            raise ValueError(f"Unsupported OAuth grant type: {grant_type}")

        try:
            oauth_req = self._session.post(
                url=self._oauth_url,
                headers=oauth_headers,
                json=oauth_body,
                timeout=30,
            )
            oauth_req.raise_for_status()
            oauth_res = oauth_req.json()

            self.access_token = oauth_res['access_token']
            self.token_type = oauth_res['token_type']
            self.refresh_token = oauth_res['refresh_token']
            self._expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=oauth_res['expires_in'])

            self._credentials_file.parent.mkdir(parents=True, exist_ok=True)
            with self._credentials_file.open("w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "access_token": self.access_token,
                    "token_type": self.token_type,
                    "refresh_token": self.refresh_token,
                    "expires_at": self._expires_at.strftime(DATE_FORMAT)
                }))

        except requests.exceptions.HTTPError as e:
            error_msg = oauth_req.json()
            raise requests.exceptions.HTTPError(f"{e} {error_msg}") from e

    def _token_is_missing(self) -> bool:
        return not self.access_token or not self.token_type or not self._expires_at

    def _token_is_expired(self) -> bool:
        expires_at = datetime.strptime(self._expires_at, DATE_FORMAT).replace(tzinfo=timezone.utc)
        return datetime.now(tz=timezone.utc) >= expires_at - timedelta(seconds=30)

    def get_access_token(self) -> tuple[str, str]:
        if self._token_is_missing() or self._token_is_expired():
            if self.refresh_token is None:
                _grant_type = "password"
            else:
                _grant_type = "refresh_token"

            self.__get_oauth_access_token(grant_type=_grant_type)

        return self.token_type, self.access_token
        
