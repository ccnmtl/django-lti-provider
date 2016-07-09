from django.conf.urls import url

from lti_provider.views import LTIConfigView, LTILandingPage, LTIRoutingView, \
    LTICourseEnableView


urlpatterns = [
    url(r'^config.xml$', LTIConfigView.as_view(), name='lti-config'),
    url(r'^landing/$', LTILandingPage.as_view(), name='lti-landing-page'),
    url(r'^enable/$', LTICourseEnableView.as_view(), name='lti-enable-course'),
    url(r'^$', LTIRoutingView.as_view(), name='lti-login'),
]
