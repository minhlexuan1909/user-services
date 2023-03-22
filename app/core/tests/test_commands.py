"""
Test custom Django management command
"""

# Mock behavior of the database connection
from unittest.mock import patch

# Exception raised by the database connection
from psycopg2 import OperationalError as PsyCopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

# Mocking check method in Command class in wait_for_db.py
@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db when db is available"""
        patched_check.return_value = True
        call_command("wait_for_db")
        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    # Keep right order of arguments
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for db when getting OperationalError"""
        # Raise exception if db is nto ready
        # The first 2 times call mock method raise PsyCopg2Error
        # The next 3 times call mock method raise OperationalError
        # These errors are raised by the stages of database creating and connecting
        patched_check.side_effect = [PsyCopg2Error] * 2 + [OperationalError] * 3 + [True]
        call_command("wait_for_db")
        # 2 (PsyCopg2Error) + 3 (OperationalError) + 1 (True) = 6
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
