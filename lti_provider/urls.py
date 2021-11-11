from django.urls import re_path

from lti_provider.views import LTIConfigView, LTILandingPage, LTIRoutingView, \
    LTICourseEnableView, LTIPostGrade, LTIFailAuthorization, LTICourseConfigure


urlpatterns = [
    re_path(r'^config.xml$', LTIConfigView.as_view(), {}, 'lti-config'),
    re_path(r'^auth$', LTIFailAuthorization.as_view(), {}, 'lti-fail-auth'),
    re_path(r'^course/config$',
            LTICourseConfigure.as_view(), {}, 'lti-course-config'),
    re_path(r'^course/enable/$',
            LTICourseEnableView.as_view(), {}, 'lti-course-enable'),
    re_path(r'^landing/$', LTILandingPage.as_view(), {}, 'lti-landing-page'),
    re_path('^grade/$', LTIPostGrade.as_view(), {}, 'lti-post-grade'),
    re_path(r'^$', LTIRoutingView.as_view(), {}, 'lti-login'),
    re_path(r'^assignment/(?P<assignment_name>.*)/(?P<pk>\d+)/$',
            LTIRoutingView.as_view(), {}, 'lti-assignment-view'),
    re_path(r'^assignment/(?P<assignment_name>.*)/$',
            LTIRoutingView.as_view(), {}, 'lti-assignment-view')
]
