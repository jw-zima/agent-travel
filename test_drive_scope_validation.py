import unittest
from types import SimpleNamespace

from tools.drive_tools import _has_required_scopes


class DriveScopeValidationTests(unittest.TestCase):
    def test_missing_drive_scopes_is_detected(self):
        creds = SimpleNamespace(scopes=["https://www.googleapis.com/auth/calendar"])
        self.assertFalse(_has_required_scopes(creds))

    def test_required_drive_scopes_are_detected(self):
        creds = SimpleNamespace(
            scopes=[
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/documents",
            ]
        )
        self.assertTrue(_has_required_scopes(creds))


if __name__ == "__main__":
    unittest.main()
