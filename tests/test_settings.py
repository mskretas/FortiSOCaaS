import os
import unittest
from unittest.mock import patch

from src.utils.settings import load_settings


class SettingsTests(unittest.TestCase):
    def test_load_settings_reads_required_environment(self):
        env = {
            "COLLECTOR_IP": "syslog_demo",
            "COLLECTOR_PORT": "5514",
            "FORTICLOUD_AUTH_URL": "http://fortiauth_demo:8000/api/v1/oauth/token/",
            "FORTINET_SOCAAS_URL": "http://fortiauth_demo:8000",
            "FORTINET_SOCAAS_API_ID": "api-id",
            "FORTINET_SOCAAS_PASSWORD": "password",
            "FORTINET_SOCAAS_CLIENT_ID": "client-id",
            "FORTINET_SOCAAS_ALLOW_INSECURE_HTTP": "true",
            "FORTINET_SOCAAS_STATE_DIR": "/tmp/socaas-state",
        }

        with patch.dict(os.environ, env, clear=True):
            settings = load_settings()

        self.assertEqual(settings.collector_ip, "syslog_demo")
        self.assertEqual(settings.collector_port, 5514)
        self.assertTrue(settings.fortinet_socaas_allow_insecure_http)
        self.assertEqual(str(settings.last_run_file), "/tmp/socaas-state/last_run.txt")
        self.assertEqual(str(settings.credentials_file), "/tmp/socaas-state/creds.json")

    def test_missing_required_environment_raises_value_error(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "COLLECTOR_IP should be defined"):
                load_settings()


if __name__ == "__main__":
    unittest.main()
