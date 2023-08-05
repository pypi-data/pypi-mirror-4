# -*- coding: utf-8 -*-
import os
from django.db import models
from django.conf import settings
from datetime import datetime
from eukalypse.eukalypse import Eukalypse


class Project(models.Model):
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    notify_mail = models.BooleanField(default=False, help_text="send notification mail after a testrun")
    notify_only_error = models.BooleanField(default=False, help_text="only send the mail if an error occurs")
    notify_recipient =  models.TextField(blank=True, null=True, help_text="Multiple recipient are ', ' (comma space) separated: mail@domain.com, mail2@domain.com")
    
    def __unicode__(self):
        return self.name


    def list_testrun_for_overview(self):
        return self.testrun.order_by('-created')[:5]
    
    
    
class Test(models.Model):
    project = models.ForeignKey('Project', related_name='tests')
    identifier = models.SlugField(max_length=200)
    url = models.URLField()
    wait = models.IntegerField(default=0, help_text="Wait xx seconds after the website finished loading to create the screenshot.")
    image = models.ImageField(upload_to='images', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%s <%s>" % (self.identifier, self.image)

    def get_identifier(self):
        from django.template.defaultfilters import slugify
        """Liefert einen identifier String für dieses Screenshotbild."""
        return u"%s" % slugify(self.identifier + "-" + str(datetime.now()).replace(' ', '-'))

    def _set_image_default(self):
        self.image = "images/default.png"
        self.save()

    def _set_image_from_url(self):
        """Erzeugt Screenshot von url mit Eukalypse und speichert selbiges image (überschreibt evtl vorhandenes image)."""
        identifier = self.get_identifier() # Vorher speichern!
        e = Eukalypse()
        e.browser = settings.EUKALYPSE_BROWSER
        e.host = settings.EUKALYPSE_HOST
        e.wait = self.wait
        e.output = os.path.join(settings.MEDIA_ROOT , 'images')
        e.screenshot(identifier, self.url)
        self.image = "images/" + identifier + ".png"
        self.save()

class Testresult(models.Model):
    test = models.ForeignKey('Test')
    testrun = models.ForeignKey('Testrun',  related_name='testresult')
    resultimage = models.ImageField(upload_to='images', null=True, blank=True)
    error = models.BooleanField(default=False)
    error_acknowledged = models.BooleanField(default=False)
    error_reference_updated = models.BooleanField(default=False)
    referenceimage = models.ImageField(upload_to='images', null=True, blank=True)
    errorimage = models.ImageField(upload_to='images', null=True, blank=True)
    errorimage_improved = models.ImageField(upload_to='images', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{0}-{1}".format(self.test.identifier, self.testrun.created)

    def become_reference(self):
        self.test.image = self.resultimage
        self.test.save()
        self.error_reference_updated=True
        self.save()
        
    def get_become_reference_url(self):
        return "/testresult/as_reference/{0}".format(self.id)
        
    def acknowledge_error(self):
        self.error_acknowledged=True
        self.save()
    
    def get_acknowledge_error_url(self):
        return "/testresult/acknowledge_error/{0}".format(self.id)

class Testrun(models.Model):
    project = models.ForeignKey('Project', null=True,  related_name='testrun')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    error = models.BooleanField(default=True)
    def __unicode__(self):
        return "{0}-{1}".format(self.project.name, self.created)

    def get_absolute_url(self):
        return "/testrun/detail/%i/" % self.id
