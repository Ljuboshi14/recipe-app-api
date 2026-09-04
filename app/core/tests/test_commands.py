"""
Test Django management commands.
"""
#mock behaviour of database  # noqa
from unittest.mock import patch 

# OperationalError one of possibilites of errors that we might get when we try to connect to database before db is ready # noqa
from psycopg2 import OperationalError as Psycopg2Error

# helper function that simulates and calls command  # noqa
from django.core.management import call_command
# what stage of process we are # noqa
from django.db.utils import OperationalError      
#testing # noqa
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """
        Test commands.
    """

    def test_wait_for_db_ready(self, patched_check):
        """
            Test waiting for database if database ready.
        """
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])
    # when adding arguments first one is looking from inside out, so first is patched_sleep then patched_check # noqa
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep , patched_check):
        """
            Test waiting for database when getting operationalError
            how mocking works when we want exeption     
            first 2 times we want Psycop2Error raised and next 3 times we want to raise OperationalError
            First stage of PostgreSQL is that app is not even started yet so its not ready to accept any connections -> Psycopg2Error
            Second stage is that db has started and ready for connections but did not set up testing database (dev database) -> Django OperationalError
        """ 
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
