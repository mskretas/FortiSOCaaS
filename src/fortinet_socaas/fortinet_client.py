from pathlib import Path
from typing import Any

from requests import Session
from requests.exceptions import HTTPError

from src.fortinet_socaas.forticloud_auth import AuthClient
from src.utils.models import Config
from src.utils.decorators import validate_request


class FortinetClient:

    def __init__(
        self,
        socaas_config: Config,
        oauth_url: str,
        credentials_file: Path,
        session: Session | None = None,
    ) -> None:

        self._url = socaas_config.formatted_url
        self._api_id = socaas_config.api_id
        self._password = socaas_config.password
        self._client_id = socaas_config.client_id
        self._session = session or Session()

        self._auth = AuthClient(
            api_id=self._api_id,
            api_password=self._password,
            api_client_id=self._client_id,
            oauth_url=oauth_url,
            credentials_file=credentials_file,
            session=self._session,
        )

        self._token_type, self._access_token = self._auth.get_access_token()


    @validate_request
    def send_request(
        self,
        http_method: str,
        http_resource: str,
        alert_uuid: str | None = None,
        service_uuid: str | None = None,
        http_version: str = "v1",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> Any:

        if http_version != "v1":
            raise ValueError('Only "v1" version is currently implemented.')

        api_base_url = self._url if not (self._url).endswith("/") else self._url[:-1]
        if alert_uuid:
            req_url = f"{api_base_url}/socaasAPI/{http_version}{http_resource}/{alert_uuid}"
        elif service_uuid:
            req_url = f"{api_base_url}/socaasAPI/{http_version}{http_resource}/{service_uuid}"
        else:
            req_url = f"{api_base_url}/socaasAPI/{http_version}{http_resource}"

        req_headers = {
            "Authorization": f"{self._token_type} {self._access_token}"
        }

        if http_resource == '/alert' and not alert_uuid:
            req_params = {
                "created_date_from": date_from,
                "created_date_to": date_to
            }
        else:
            req_params = {}

        try:
            new_req = self._session.request(
                method=http_method,
                url=req_url,
                params=req_params,
                headers=req_headers,
                timeout=30,
            )
            new_req.raise_for_status()

            return new_req.json()

        except HTTPError as e:
            error_msg = new_req.json()
            raise HTTPError(f"{e} {error_msg}") from e
