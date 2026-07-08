import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_STATE_DIR = Path("/app/state")


@dataclass(frozen=True)
class Settings:
    collector_ip: str
    collector_port: int
    forticloud_auth_url: str
    fortinet_socaas_url: str
    fortinet_socaas_api_id: str
    fortinet_socaas_password: str
    fortinet_socaas_client_id: str
    fortinet_socaas_allow_insecure_http: bool
    state_dir: Path

    @property
    def last_run_file(self) -> Path:
        return self.state_dir / "last_run.txt"

    @property
    def credentials_file(self) -> Path:
        return self.state_dir / "creds.json"


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} should be defined.")
    return value


def _optional_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    return Settings(
        collector_ip=_required_env("COLLECTOR_IP"),
        collector_port=int(_required_env("COLLECTOR_PORT")),
        forticloud_auth_url=_required_env("FORTICLOUD_AUTH_URL"),
        fortinet_socaas_url=_required_env("FORTINET_SOCAAS_URL"),
        fortinet_socaas_api_id=_required_env("FORTINET_SOCAAS_API_ID"),
        fortinet_socaas_password=_required_env("FORTINET_SOCAAS_PASSWORD"),
        fortinet_socaas_client_id=_required_env("FORTINET_SOCAAS_CLIENT_ID"),
        fortinet_socaas_allow_insecure_http=_optional_bool_env("FORTINET_SOCAAS_ALLOW_INSECURE_HTTP"),
        state_dir=Path(os.getenv("FORTINET_SOCAAS_STATE_DIR", str(DEFAULT_STATE_DIR))),
    )
