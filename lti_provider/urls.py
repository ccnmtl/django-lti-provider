from django.conf.urls import url

from lti_provider.views import LTIConfigView, LTILandingPage, LTIRoutingView, \
    LTICourseEnableView, LTIPostGrade


urlpatterns = [
    url(r'^config.xml$', LTIConfigView.as_view(), {}, 'lti-config'),
    url(r'^enable/$', LTICourseEnableView.as_view(), {}, 'lti-enable-course'),
    url(r'^landing/(?P<context>\w[^/]*)/$',
        LTILandingPage.as_view(), {}, 'lti-landing-page'),
    url('^grade/$', LTIPostGrade.as_view(), {}, 'lti-post-grade'),
    url(r'^$', LTIRoutingView.as_view(), {}, 'lti-login'),
]
