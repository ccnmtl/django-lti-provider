from django.contrib.sessions.middleware import SessionMiddleware
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory, Client
from lti_provider.lti import LTI
from lti_provider.tests.factories import LTICourseContextFactory, \
    UserFactory, CONSUMERS, generate_lti_request, BASE_LTI_PARAMS
from lti_provider.views import LTIAuthMixin, LTIRoutingView
from pylti.common import LTI_SESSION_KEY

import xml.etree.ElementTree as ET

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
    'new_tab': False,
    'allow_ta_access': False
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

    def test_join_groups_student(self):
        mixin = LTIAuthMixin()
        ctx = LTICourseContextFactory()
        user = UserFactory()
        self.request.user = user

        with self.settings(
                LTI_TOOL_CONFIGURATION=TEST_LTI_TOOL_CONFIGURATION):
            self.request.session['roles'] = u'Learner'
            mixin.join_groups(self.request, self.lti, ctx)
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertFalse(user in ctx.faculty_group.user_set.all())

    def test_join_groups_teachingassistant_false(self):
        mixin = LTIAuthMixin()
        ctx = LTICourseContextFactory()
        user = UserFactory()
        self.request.user = user
        lti_tool_config1 = TEST_LTI_TOOL_CONFIGURATION.copy()

        with self.settings(
                LTI_TOOL_CONFIGURATION=lti_tool_config1):
            self.request.session['roles'] = \
                u'urn:lti:role:ims/liss/TeachingAssistant'
            mixin.join_groups(self.request, self.lti, ctx)
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertFalse(user in ctx.faculty_group.user_set.all())

    def test_join_groups_teachingassistant_true(self):
        mixin = LTIAuthMixin()
        ctx = LTICourseContextFactory()
        user = UserFactory()
        self.request.user = user
        lti_tool_config2 = TEST_LTI_TOOL_CONFIGURATION.copy()
        lti_tool_config2['allow_ta_access'] = True

        with self.settings(
                LTI_TOOL_CONFIGURATION=lti_tool_config2):
            self.request.session['roles'] = \
                u'urn:lti:role:ims/lis/TeachingAssistant'
            mixin.join_groups(self.request, self.lti, ctx)
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertTrue(user in ctx.faculty_group.user_set.all())

    def test_missing_configuration(self):
        mixin = LTIAuthMixin()
        ctx = LTICourseContextFactory()
        user = UserFactory()
        self.request.user = user
        lti_tool_config2 = TEST_LTI_TOOL_CONFIGURATION.copy()
        del lti_tool_config2['allow_ta_access']

        with self.settings(
                LTI_TOOL_CONFIGURATION=lti_tool_config2):
            self.request.session['roles'] = \
                u'urn:lti:role:ims/lis/TeachingAssistant'
            mixin.join_groups(self.request, self.lti, ctx)
            self.assertTrue(user in ctx.group.user_set.all())
            self.assertFalse(user in ctx.faculty_group.user_set.all())

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

    def test_course_navigation(self):
        with self.settings(
                LTI_TOOL_CONFIGURATION=TEST_LTI_TOOL_CONFIGURATION):

            client = Client()
            response = client.get('/lti/config.xml')
            config_xml = response.content.decode()

            root = ET.fromstring(config_xml)
            course_navigation_property = root.find(
                    ".//*[@name='course_navigation']")
            enabled = course_navigation_property.find(
                    "./*[@name='enabled']").text

            self.assertEqual(enabled, 'true')

    def test_course_navigation_as_dict(self):
        lti_tool_config = TEST_LTI_TOOL_CONFIGURATION
        lti_tool_config['course_navigation'] = {
            "default": "disabled",
            "enabled": "true",
            "windowTarget": "_blank"
        }
        with self.settings(
                LTI_TOOL_CONFIGURATION=lti_tool_config):

            client = Client()
            response = client.get('/lti/config.xml')
            config_xml = response.content.decode()

            root = ET.fromstring(config_xml)
            course_navigation_property = root.find(
                    ".//*[@name='course_navigation']")
            window_target = course_navigation_property.find(
                    "./*[@name='windowTarget']").text

            self.assertEqual(window_target, '_blank')

    def test_lookup_assignment_name(self):
        lti_tool_config = TEST_LTI_TOOL_CONFIGURATION
        lti_tool_config['assignments'] = {
            '1': '/assignment/1/'
        }
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS},
                           LTI_TOOL_CONFIGURATION=lti_tool_config):

            view = LTIRoutingView()
            assignment = view.lookup_assignment_name('1', '1')
            self.assertEqual(assignment, '/assignment/1/')
