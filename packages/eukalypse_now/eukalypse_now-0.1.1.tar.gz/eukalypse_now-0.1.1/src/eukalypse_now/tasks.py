# -*- coding: utf-8 -*-
# 
from celery.task import  task, Task
from django.core.management import call_command
from models import Project
import  logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from eukalypse_now.models import Project
from eukalypse_now.models import Testresult
from eukalypse_now.models import Testrun
from eukalypse.eukalypse import Eukalypse
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText


logger = logging.getLogger('eukalypse-now.task')

class PeriodicalCheck(Task):
    """ Task to automatically check all the active projects and run the testruns one after another."""
    def run(self, **kwargs):
        logger.debug("run PeriodicalCheck")
        for project in Project.objects.filter(active=True):
            logger.error(project)
            call_command("testrun", project.name)


class SetImageFromUrl(Task):

    def run(self, instance, **kwargs):
        logger.debug("run SetImageFromUrl")

        instance._set_image_from_url()


class Testrunner(Task):
    def _getMediaUrl(self, path):
        return path[len(settings.MEDIA_ROOT):]

    def run(self, arg_project = None, *args, **options):
        project =  Project.objects.get(name=arg_project)
        testrun = Testrun.objects.create(project=project)
        for test in project.tests.all():

            e = Eukalypse()
            e.browser = settings.EUKALYPSE_BROWSER
            e.host = settings.EUKALYPSE_HOST
            e.wait=test.wait
            e.output = os.path.join(settings.MEDIA_ROOT , 'images')
            eukalypse_result_object = e.compare(test.get_identifier(), test.image, test.url)
            e.disconnect()
            if eukalypse_result_object.clean:
                testresult = Testresult.objects.create(\
                    test=test, \
                    testrun = testrun, \
                    error = False, \
                    resultimage=self._getMediaUrl(eukalypse_result_object.target_img),\
                    referenceimage=test.image, \
                    )
            else:
                testresult = Testresult.objects.create(\
                    test=test, \
                    testrun = testrun, \
                    error = True, \
                    resultimage=self._getMediaUrl(eukalypse_result_object.target_img), \
                    referenceimage=test.image, \
                    errorimage=self._getMediaUrl(eukalypse_result_object.difference_img), \
                    errorimage_improved=self._getMediaUrl(eukalypse_result_object.difference_img_improved)\
                    )
                testrun.error = True

            testresult.save()

        testrun.save()

        if project.notify_mail:
            if (project.notify_only_error and testrun.error) or not project.notify_only_error:
                from django.template.loader import render_to_string
                render = render_to_string('eukalypse_now/mail.html', {'testrun': testrun, 'SITE_URL': settings.SITE_URL})
                msg = MIMEText(render, 'html')
                msg['Subject'] = 'Pixel Reporting'
                msg['From'] = settings.NOTIFY_MAIL_SENDER
                msg['To'] = project.notify_recipient
                s = smtplib.SMTP(settings.EMAIL_HOST)
                rcpts = [r.strip() for r in  project.notify_recipient.split(',') if r]
                s.sendmail(settings.NOTIFY_MAIL_SENDER, rcpts, msg.as_string())
                s.quit()



