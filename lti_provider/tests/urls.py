from __future__ import unicode_literals

from django.urls import include, path


urlpatterns = [
    path('lti/', include('lti_provider.urls'))
]
