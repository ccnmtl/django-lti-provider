from __future__ import unicode_literals

from django.conf.urls import include, url


urlpatterns = [
    url(r'^lti/', include('lti_provider.urls'))
]
