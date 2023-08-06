from django.conf.urls import include, patterns, url

from urls import services

urlpatterns = patterns('',
    url(r'^', include(services.urls)),
)


