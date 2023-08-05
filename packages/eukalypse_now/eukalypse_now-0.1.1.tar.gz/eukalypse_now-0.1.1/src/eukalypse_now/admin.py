# -*- coding: utf-8 -*-
import os
from django.contrib import admin
from django.conf import settings
# Eukalypse Imports
from models import Test, Project, Testrun, Testresult
from eukalypse.eukalypse import Eukalypse


class TestInline(admin.StackedInline):
    model = Test
    extra = 0

class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'active']}),
        ('Notification Mail',               {'fields': ['notify_mail', 'notify_only_error', 'notify_recipient']}),
    ]
    inlines = [TestInline]
    list_display = ('name', 'active', )
    def save_formset(self, request, form, formset, change):
        """ Speichert Screenshots der tests als Referenz, wenn noch kein Bild Hinterlegt.
        Damit das auch beim anlegen neuer Tests und speichern bestehnder funktioniert
        wird jedesmal über das formset iteriert und in jedem Test der kein Bild hat 
        das bild neu erzeugt und gespeichert.
        """
        formset.save()
        for f in formset.forms:
            if not f.instance.image:
                #the default images has some advantages to a "None" Image. the most important one is: 
                #if you save twice and the first save is not finished creating the image, the second save will not trigger another image creation because an image - the default one- is already set. 
                f.instance._set_image_default()
                from eukalypse_now.tasks import SetImageFromUrl 
                SetImageFromUrl.delay(f.instance)


admin.site.register(Project, ProjectAdmin)


admin.site.register(Test)
admin.site.register(Testrun)
admin.site.register(Testresult)

