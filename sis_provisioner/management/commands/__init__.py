# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.mail import send_mail
from sis_provisioner.dao import is_using_file_dao
from sis_provisioner.util.settings import get_cronjob_sender


def send_msg(logger, source, msg):
    logger.error(msg)
    if is_using_file_dao():
        return
    sender = get_cronjob_sender()
    try:
        send_mail(source, msg, sender, [sender])
    except Exception as ex:
        logger.error({"Source": source, "Error": ex})
