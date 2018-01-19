from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from lti_provider.lti import LTI
from lti_provider.tests.factories import BASE_LTI_PARAMS, CONSUMERS, \
    generate_lti_request
from pylti.common import LTI_SESSION_KEY, LTINotInSessionException


class LTITest(TestCase):

    def setUp(self):
        self.request = RequestFactory()
        self.request.COOKIES = {}
        middleware = SessionMiddleware()
        middleware.process_request(self.request)
        self.request.session.save()

        for prop, value in BASE_LTI_PARAMS.items():
            self.request.session[prop] = value

        self.lti = LTI('initial', 'any')

        self.emptyRequest = RequestFactory()
        self.emptyRequest.COOKIES = {}
        middleware = SessionMiddleware()
        middleware.process_request(self.emptyRequest)
        self.emptyRequest.session.save()

    def test_init(self):
        self.assertEquals(self.lti.request_type, 'initial')
        self.assertEquals(self.lti.role_type, 'any')

    def test_consumer_user_id(self):
        self.request.session['oauth_consumer_key'] = '1234567890'
        self.assertEquals(
            self.lti.consumer_user_id(self.request), '1234567890-student')

    def test_user_email(self):
        self.assertIsNone(self.lti.user_email(self.emptyRequest))
        self.assertEquals(self.lti.user_email(self.request), 'foo@bar.com')

    def test_user_fullname(self):
        self.assertEquals(self.lti.user_fullname(self.emptyRequest), '')

        self.assertEquals(self.lti.user_fullname(self.request), 'Foo Bar Baz')

    def test_user_roles(self):
        self.assertEquals(self.lti.user_roles(self.emptyRequest), [])

        self.assertEquals(self.lti.user_roles(self.request), [
            u'urn:lti:instrole:ims/lis/instructor',
            u'urn:lti:instrole:ims/lis/staff'])

        self.assertTrue(self.lti.is_instructor(self.request))
        self.assertFalse(self.lti.is_administrator(self.request))

    def test_consumers(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            self.assertEquals(self.lti.consumers(), CONSUMERS)

    def test_params(self):
        factory = RequestFactory()
        request = factory.post('/', {'post': 'data'})
        params = self.lti._params(request)
        self.assertTrue('post' in params)

        request = factory.post('/', {'get': 'data'})
        params = self.lti._params(request)
        self.assertTrue('get' in params)

    def test_verify_any(self):
        lti = LTI('any', 'any')
        request = generate_lti_request()

        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            # test_verify_request
            lti.verify(request)
            self.assertTrue(request.session[LTI_SESSION_KEY])

            # test_verify_session
            self.assertTrue(lti.verify(request))

    def test_verify_session(self):
        lti = LTI('session', 'any')
        request = RequestFactory().post('/lti/')

        with self.assertRaises(LTINotInSessionException):
            request.session = {}
            lti.verify(request)

        request.session = {LTI_SESSION_KEY: True}
        self.assertTrue(lti.verify(request))

    def test_verify_request(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            request = generate_lti_request()
            lti = LTI('initial', 'any')
            lti.verify(request)
            self.assertTrue(request.session[LTI_SESSION_KEY])
