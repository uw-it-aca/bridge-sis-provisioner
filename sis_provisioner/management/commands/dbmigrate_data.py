# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import os
from django.db import connections
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.models import UwAccount


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'action', choices=['all', 'prep', 'dump', 'load', 'inspect'])

    def handle(self, *args, **options):
        self.fixture_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'mysql_data_fixture.json')

        self.action = options['action']

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
        # os.remove(self.fixture_file)

    def before_dump(self):
        logger.info("{} UwAccounts in mysql DB".format(
            len(UwAccount.objects.using('mysql').all())))
        # with connections['mysql'].cursor() as cursor:
        # cursor.execute("DELETE FROM django_session")

    def dump_mysql_data(self):
        if os.path.exists(self.fixture_file):
            os.remove(self.fixture_file)
        try:
            model_list = ['sis_provisioner.UwAccount']
            call_command(
                'dumpdata', *model_list, '--database=mysql',
                output=self.fixture_file)
        except CommandError as e:
            logger.error("Dump table from the MySQL DB: {}".format(e))

    def load_postgresdb(self):
        try:
            call_command('loaddata', self.fixture_file)
        except CommandError as e:
            logger.error("Load data into Postgres DB: {}".format(e))

    def inspect_postgresqldb(self):
        logger.info("{} UwAccount loaded".format(
            len(UwAccount.objects.all())))
