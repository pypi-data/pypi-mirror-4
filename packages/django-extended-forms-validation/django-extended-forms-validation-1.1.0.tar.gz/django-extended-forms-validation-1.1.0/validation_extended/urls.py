from django.conf.urls import patterns, url


urlpatterns = patterns(
    'validation_extended.views',
    url(r'^validate/?$', 'remote_validation'))
