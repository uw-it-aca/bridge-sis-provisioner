# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import os
from django.db import connections
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


fixture_file = 'mysql_data_fixture.json'
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'action', choices=['all', 'prep', 'dump', 'load', 'inspect'])

    def handle(self, *args, **options):
        self.action = options['action']
        os.remove(fixture_file)

        if self.action == 'dump':
            self.dump_mysql_data()
        if self.action == 'load':
            self.load_postgresdb()
        if self.action == 'inspect':
            self.inspect_postgresqldb()
        if self.action == 'prep':
            self.before_dump()
        if self.action == 'all':
            self.before_dump()
            self.dump_mysql_data()
            self.load_postgresdb()
            self.inspect_postgresqldb()

        # Cleanup: Delete the local fixture file
        # os.remove(fixture_file)

    def before_dump(self):
        with connections['mysql'].cursor() as cursor:
            cursor.execute("DELETE FROM django_session")

    def dump_mysql_data(self):
        try:
            call_command('dumpdata', '--database=mysql', output=fixture_file)
        except CommandError as e:
            logger.error("Dump table from the MySQL DB: {}".format(e))

    def load_postgresdb(self):
        try:
            call_command('loaddata', fixture_file)
        except CommandError as e:
            logger.error("Load data into Postgres DB: {}".format(e))

    def inspect_postgresqldb(self):
        call_command('inspectdb')
