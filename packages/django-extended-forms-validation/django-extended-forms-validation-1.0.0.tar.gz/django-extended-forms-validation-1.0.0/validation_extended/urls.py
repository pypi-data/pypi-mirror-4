from django.conf.urls import patterns, url


urlpatterns = patterns(
    'extended_validation.views',
    url(r'^validate/?$', 'remote_validation'))
