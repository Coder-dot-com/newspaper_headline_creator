"""
Django command to wait for the database to be available.
"""
import time

from psycopg import OperationalError as Psycopg3OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

from django.db import connection

class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write('Waiting for database connection...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg3OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        db_name = connection.settings_dict['NAME']
        self.stdout.write(self.style.SUCCESS(f'Database connected! {db_name}'))