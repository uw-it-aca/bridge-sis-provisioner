# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import subprocess
from django.core.management.base import BaseCommand


fixture_file = 'mysql_data_fixture.json'
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'action', choices=['all', 'dump', 'load', 'inspect'])

    def handle(self, *args, **options):
        self.action = options['action']
        os.remove(fixture_file)

        if self.action == 'dump':
            self.dump_mysql_data()
        if self.action == 'load':
            self.load_data_into_postgresql()
        if self.action == 'inspect':
            self.inspect_postgresqldb()
        if self.action == 'all':
            self.dump_mysql_data()
            self.load_data_into_postgresql()
            self.inspect_postgresqldb()

        # Cleanup: Delete the local fixture file
        # os.remove(fixture_file)

    def dump_mysql_data(self):
        load_data_command = f'python manage.py dumpdata -o {fixture_file} --database=mysql'
        subprocess.run(load_data_command, shell=True, check=True)
        #call_command('dumpdata', '--database=mysql', output=fixture_file)
        print("MySQL data dumped to fixture file")

    def load_data_into_postgresql(self):
        load_data_command = f'python manage.py loaddata {fixture_file} --database=default'
        subprocess.run(load_data_command, shell=True, check=True)
        print("Data loaded into PostgreSQL database")

    def inspect_postgresqldb(self):
        load_data_command = f'python manage.py inspectdb --database=default'
        subprocess.run(load_data_command, shell=True, check=True)
