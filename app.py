import os
import sys
from datetime import datetime, timezone, timedelta

from src.utils.models import Config
from src.utils.loggers import app_logger, syslog_root_logger
from src.fortinet_socaas.FortiNet_Client import FortinetClient



co = Config (
    url = "https://tel",
    api_id =  "tel2",
    password = "tel3",
    client_id = "tel4"
    )

try:
    collector_ip = os.getenv("COLLECTOR_IP")
    collector_port = os.getenv("COLLECTOR_PORT")

    if not collector_ip or not collector_port:
        raise ValueError("COLLECTOR_IP and COLLECTOR_PORT should be defined.")
    
    syslog_logger = syslog_root_logger(collector_ip=collector_ip, collector_port=collector_port)

    date_to = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    with open("last_run.txt", "r") as f:
        date_from = f.read()
    
except FileNotFoundError:
    date_from = (datetime.now(tz=timezone.utc) - timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
    app_logger.info(f"Running for first time. UTC time started collecting alerts \"{date_from}\".")

except Exception as e:
    app_logger.error(e)
    sys.exit(-1)


def main():
    try:
        # client = FortinetClient(socaas_config=co)
        # print(client._url)

        print(date_from)

        # client.send_request(httpMethod='GET', httpResource='/alerts')

        with open("last_run.txt", "w") as f:
            f.write(date_to)

    except Exception as e:
        app_logger.error(e)
        # print(e)


if __name__ == "__main__":
    main()