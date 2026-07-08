import sys
import logging
from logging.handlers import SysLogHandler


formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

def _stdout_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

    return logger


app_logger = _stdout_logger("fortinet_socaas.app")


class RaisingSysLogHandler(SysLogHandler):
    def handleError(self, record):
        exc = sys.exc_info()[1]
        if exc:
            raise exc
        raise RuntimeError("Syslog handler failed.")
    
def syslog_root_logger(collector_ip: str, collector_port: int) -> logging.Logger:
    syslog_logger = logging.getLogger(name="fortinet_socaas.syslog")
    syslog_logger.setLevel(logging.INFO)
    syslog_logger.propagate = False

    syslog_handler = RaisingSysLogHandler(
        address=(str(collector_ip), int(collector_port)),
        facility=SysLogHandler.LOG_USER,
    )

    syslog_handler.setLevel(logging.INFO)
    if not syslog_logger.handlers:
        syslog_logger.addHandler(syslog_handler)

    return syslog_logger
