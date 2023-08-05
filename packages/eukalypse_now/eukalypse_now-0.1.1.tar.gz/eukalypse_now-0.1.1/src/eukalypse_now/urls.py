from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eukalypse_now.views.home', name='home'),
    url(r'^testrun/list/', 'eukalypse_now.views.testrun_list'),
    url(r'^testrun/detail/(?P<testrun_id>\d+)/', 'eukalypse_now.views.testrun_detail'),
    url(r'^testresult/as_reference/(?P<testresult_id>\d+)/', 'eukalypse_now.views.testresult_as_reference'),
    url(r'^testresult/acknowledge_error/(?P<testresult_id>\d+)/', 'eukalypse_now.views.testresult_acknowledge_error'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
    url(r'^$', 'eukalypse_now.views.testrun_list'),
)
urlpatterns += staticfiles_urlpatterns()
