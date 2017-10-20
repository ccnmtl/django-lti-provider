from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from lti_provider.auth import LTIBackend
from lti_provider.lti import LTI
from lti_provider.tests.factories import BASE_LTI_PARAMS, UserFactory


class LTIBackendTest(TestCase):

    def setUp(self):
        self.backend = LTIBackend()

        self.request = RequestFactory()
        self.request.COOKIES = {}
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()

        for prop, value in BASE_LTI_PARAMS.items():
            self.request.session[prop] = value

        self.lti = LTI('initial', 'any')

    def test_create_user(self):
        user = self.backend.create_user(self.request, self.lti, '12345')
        self.assertFalse(user.has_usable_password())
        self.assertEquals(user.email, 'foo@bar.com')
        self.assertEquals(user.get_full_name(), 'Foo Baz')

    def test_create_user_no_full_name(self):
        self.request.session.pop('lis_person_name_full')
        user = self.backend.create_user(self.request, self.lti, '12345')
        self.assertEquals(user.get_full_name(), 'student')

    def test_create_user_empty_full_name(self):
        self.request.session['lis_person_name_full'] = ''
        user = self.backend.create_user(self.request, self.lti, '12345')
        self.assertEquals(user.get_full_name(), 'student')

    def test_create_user_long_name(self):
        self.request.session['lis_person_name_full'] = (
            'Pneumonoultramicroscopicsilicovolcanoconiosis '
            'Supercalifragilisticexpialidocious')
        user = self.backend.create_user(self.request, self.lti, '12345')
        self.assertEquals(
            user.get_full_name(),
            'Pneumonoultramicroscopicsilico Supercalifragilisticexpialidoc')

    def test_find_or_create_user1(self):
        # via email
        user = UserFactory(email='foo@bar.com')
        self.assertEquals(
            self.backend.find_or_create_user(self.request, self.lti), user)

    def test_find_or_create_user2(self):
        # via lms username
        username = 'uni123'
        self.request.session['custom_canvas_user_login_id'] = username
        user = UserFactory(username=username)
        self.assertEquals(
            self.backend.find_or_create_user(self.request, self.lti), user)

    def test_find_or_create_user3(self):
        # via hashed username
        self.request.session['oauth_consumer_key'] = '1234567890'
        username = self.backend.get_hashed_username(self.request, self.lti)
        user = UserFactory(username=username)
        self.assertEquals(
            self.backend.find_or_create_user(self.request, self.lti), user)

    def test_find_or_create_user4(self):
        # new user
        self.request.session['oauth_consumer_key'] = '1234567890'
        user = self.backend.find_or_create_user(self.request, self.lti)
        self.assertFalse(user.has_usable_password())
        self.assertEquals(user.email, 'foo@bar.com')
        self.assertEquals(user.get_full_name(), 'Foo Baz')

        username = self.backend.get_hashed_username(self.request, self.lti)
        self.assertEquals(user.username, username)

    def test_get_user(self):
        user = UserFactory()
        self.assertIsNone(self.backend.get_user(1234))
        self.assertEquals(self.backend.get_user(user.id), user)
