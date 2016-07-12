import csv
import logging
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.load_users import LoadUsers


OUTPUT_FORMAT = "uid,regid,first_name,last_name,display_name,email" +\
    "home_department,is_alum,is_employee,is_faculty,is_staff,is_student"
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Build the csv file  for upload users into BridgeApp'
    args = "<full path file name>"

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("Invalid parameter %s" % args)

        load_users = LoadUsers()
        load_users.fetch_all()

        if load_users.get_user_count() == 0:
            print "No user found, abort!"

        outfile = args[0]

        f = open(outfile, 'w')
        f.write("%s\n" % OUTPUT_FORMAT)
        
        for user in load_users.get_users():
            if len(user.home_department)> 0:
                home_dept = user.home_department
            else:
                home_dept = ""

            f.write(','.join([user.netid + "@washington.edu",
                              user.regid,
                              user.first_name,
                              user.last_name,
                              user.display_name,
                              user.email,
                              home_dept,
                              'alumni' if user.is_alum else "",
                              'employee' if user.is_employee else "",
                              'faculty' if user.is_faculty else "",
                              'staff' if user.is_staff else "",
                              'student' if user.is_student else "",
                              ]))
            f.write("\n")
        f.close()
