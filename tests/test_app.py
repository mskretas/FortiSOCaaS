import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app import _extract_alerts, _read_last_run


class AppTests(unittest.TestCase):
    def test_read_last_run_defaults_to_previous_five_minutes(self):
        now = datetime(2026, 7, 5, 12, 0, 0, tzinfo=timezone.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            last_run = Path(tmpdir) / "last_run.txt"
            self.assertEqual(_read_last_run(last_run, now), "2026-07-05T11:55:00Z")

    def test_read_last_run_uses_existing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            last_run = Path(tmpdir) / "last_run.txt"
            last_run.write_text("2026-07-05T11:58:00Z", encoding="utf-8")

            result = _read_last_run(last_run, datetime.now(tz=timezone.utc))

        self.assertEqual(result, "2026-07-05T11:58:00Z")

    def test_extract_alerts_supports_api_response_shape(self):
        alert = {"uuid": "alert-1"}

        self.assertEqual(_extract_alerts({"result": {"data": [alert]}}), [alert])

    def test_extract_alerts_rejects_unexpected_shape(self):
        with self.assertRaisesRegex(TypeError, "Unexpected alert response type"):
            _extract_alerts("bad response")


if __name__ == "__main__":
    unittest.main()
