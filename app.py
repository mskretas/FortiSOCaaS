import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from src.utils.models import Config
from src.utils.settings import load_settings
from src.utils.loggers import app_logger, syslog_root_logger
from src.fortinet_socaas.fortinet_client import FortinetClient


DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _read_last_run(last_run_file: Path, now: datetime) -> str:
    try:
        date_from = last_run_file.read_text(encoding="utf-8").strip()
        if not date_from:
            raise ValueError(f"{last_run_file} is empty.")
        return date_from
    except FileNotFoundError:
        date_from = (now - timedelta(minutes=5)).strftime(DATE_FORMAT)
        app_logger.info(f'Running for first time. UTC time started collecting alerts "{date_from}".')
        return date_from


def _extract_alerts(response: Any) -> list[Any]:
    if isinstance(response, list):
        return response
    if isinstance(response, dict):
        return response.get("result", {}).get("data", [])
    raise TypeError(f"Unexpected alert response type: {type(response).__name__}")


def main() -> None:
    try:
        settings = load_settings()
        config = Config(
            url=settings.fortinet_socaas_url,
            api_id=settings.fortinet_socaas_api_id,
            password=settings.fortinet_socaas_password,
            client_id=settings.fortinet_socaas_client_id,
            allow_insecure_http=settings.fortinet_socaas_allow_insecure_http,
        )

        settings.state_dir.mkdir(parents=True, exist_ok=True)

        syslog_logger = syslog_root_logger(
            collector_ip=settings.collector_ip,
            collector_port=settings.collector_port,
        )
        now = datetime.now(tz=timezone.utc)
        date_to = now.strftime(DATE_FORMAT)
        date_from = _read_last_run(settings.last_run_file, now)

        client = FortinetClient(
            socaas_config=config,
            oauth_url=settings.forticloud_auth_url,
            credentials_file=settings.credentials_file,
        )
        app_logger.info(f"Collecting alerts from {date_from} to {date_to}.")

        response = client.send_request(
            http_method="GET",
            http_resource="/alert",
            date_from=date_from,
            date_to=date_to,
        )

        all_alerts = _extract_alerts(response)

        for alert in all_alerts:
            syslog_logger.info(json.dumps(alert))

        settings.last_run_file.write_text(date_to, encoding="utf-8")
        app_logger.info(f"Forwarded {len(all_alerts)} alerts. Updated last_run to {date_to}.")

        sys.exit(0)
    except Exception as e:
        app_logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
