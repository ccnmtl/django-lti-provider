from django.urls import path, re_path

from lti_provider.views import (
    LTIConfigView, LTILandingPage, LTIRoutingView,
    LTICourseEnableView, LTIPostGrade, LTIFailAuthorization,
    LTICourseConfigure,
    login, launch, get_jwks, configure
)


urlpatterns = [
    path('config.xml', LTIConfigView.as_view(), {}, 'lti-config'),
    path('auth', LTIFailAuthorization.as_view(), {}, 'lti-fail-auth'),
    path('course/config',
         LTICourseConfigure.as_view(), {}, 'lti-course-config'),
    path('course/enable/',
         LTICourseEnableView.as_view(), {}, 'lti-course-enable'),
    path('landing/', LTILandingPage.as_view(), {}, 'lti-landing-page'),
    path('grade/', LTIPostGrade.as_view(), {}, 'lti-post-grade'),
    path('', LTIRoutingView.as_view(), {}, 'lti-login'),
    re_path(r'^assignment/(?P<assignment_name>.*)/(?P<pk>\d+)/$',
            LTIRoutingView.as_view(), {}, 'lti-assignment-view'),
    re_path(r'^assignment/(?P<assignment_name>.*)/$',
            LTIRoutingView.as_view(), {}, 'lti-assignment-view'),

    # New pylti1.3 routes
    path('login/', login, name='lti-login'),
    path('launch/', launch, name='lti-launch'),
    path('jwks/', get_jwks, name='jwks'),
    re_path(r'^configure/(?P<launch_id>[\w-]+)/$', configure,
            name='lti-configure')
]
