from django.contrib.sessions.middleware import SessionMiddleware
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from lti_provider.lti import LTI
from lti_provider.tests.factories import LTICourseContextFactory, \
    UserFactory, CONSUMERS, generate_lti_request, BASE_LTI_PARAMS
from lti_provider.views import LTIAuthMixin, LTIRoutingView
from pylti.common import LTI_SESSION_KEY


TEST_LTI_TOOL_CONFIGURATION = {
    'title': 'Test Application',
    'description': 'Test Description.',
    'launch_url': 'lti/',
    'embed_url': 'asset/embed/',
    'embed_icon_url': '',
    'embed_tool_id': '',
    'landing_url': '{}://{}/',
    'course_aware': True,
    'course_navigation': True,
    'new_tab': False
}


class LTIViewTest(TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.request.COOKIES = {}
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()

        for prop, value in BASE_LTI_PARAMS.items():
            self.request.session[prop] = value

        self.lti = LTI('initial', 'any')

    def test_join_groups(self):
        mixin = LTIAuthMixin()
        ctx = LTICourseContextFactory()
        user = UserFactory()
        self.request.user = user

        mixin.join_groups(self.request, self.lti, ctx)
        self.assertTrue(user in ctx.group.user_set.all())
        self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_launch_invalid_user(self):
        request = generate_lti_request()

        response = LTIRoutingView().dispatch(request)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(response.url, reverse('lti-fail-auth'))
        self.assertFalse(request.session.get(LTI_SESSION_KEY, False))

    def test_launch_invalid_course(self):
        with self.settings(
            LTI_TOOL_CONFIGURATION=TEST_LTI_TOOL_CONFIGURATION,
                PYLTI_CONFIG={'consumers': CONSUMERS}):
            request = generate_lti_request()

            response = LTIRoutingView().dispatch(request)
            self.assertEquals(response.status_code, 302)
            self.assertEquals(response.url, reverse('lti-course-config'))
            self.assertTrue(request.session.get(LTI_SESSION_KEY, False))

    def test_launch(self):
        with self.settings(
            LTI_TOOL_CONFIGURATION=TEST_LTI_TOOL_CONFIGURATION,
            PYLTI_CONFIG={'consumers': CONSUMERS},
                LTI_EXTRA_PARAMETERS=['lti_version']):
            ctx = LTICourseContextFactory()
            request = generate_lti_request(ctx)

            view = LTIRoutingView()
            view.request = request

            response = view.dispatch(request)
            self.assertEquals(response.status_code, 302)

            landing = 'http://testserver/?lti_version=LTI-1p0&'
            self.assertEquals(
                response.url, landing.format(ctx.lms_course_context))

            self.assertIsNotNone(request.session[LTI_SESSION_KEY])
            user = request.user
            self.assertFalse(user.has_usable_password())
            self.assertEquals(user.email, 'foo@bar.com')
            self.assertEquals(user.get_full_name(), 'Foo Baz')
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_launch_custom_landing_page(self):
        with self.settings(
            LTI_TOOL_CONFIGURATION=TEST_LTI_TOOL_CONFIGURATION,
            PYLTI_CONFIG={'consumers': CONSUMERS},
                LTI_EXTRA_PARAMETERS=['lti_version']):
            ctx = LTICourseContextFactory()
            request = generate_lti_request(ctx, 'canvas')

            view = LTIRoutingView()
            view.request = request

            response = view.dispatch(request)
            landing = 'http://testserver/lti/landing/{}/?lti_version=LTI-1p0&'
            self.assertEquals(response.status_code, 302)
            self.assertTrue(
                response.url,
                landing.format(ctx.lms_course_context))

            self.assertIsNotNone(request.session[LTI_SESSION_KEY])
            user = request.user
            self.assertFalse(user.has_usable_password())
            self.assertEquals(user.email, 'foo@bar.com')
            self.assertEquals(user.get_full_name(), 'Foo Baz')
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_embed(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS},
                           LTI_EXTRA_PARAMETERS=['lti_version'],
                           LTI_TOOL_CONFIGURATION=TEST_LTI_TOOL_CONFIGURATION):
            ctx = LTICourseContextFactory()
            request = generate_lti_request(ctx, 'canvas', 'embed')

            view = LTIRoutingView()
            view.request = request

            response = view.dispatch(request)
            self.assertEquals(response.status_code, 302)
            self.assertEquals(
                response.url,
                'http://testserver/asset/embed/?return_url=/asset/'
                '&lti_version=LTI-1p0&')

            self.assertIsNotNone(request.session[LTI_SESSION_KEY])
            user = request.user
            self.assertFalse(user.has_usable_password())
            self.assertEquals(user.email, 'foo@bar.com')
            self.assertEquals(user.get_full_name(), 'Foo Baz')
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())
