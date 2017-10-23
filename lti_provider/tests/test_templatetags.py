from django.test.testcases import TestCase
from lti_provider.lti import LTI
from lti_provider.templatetags.lti_utils import lti_session
from lti_provider.tests.factories import CONSUMERS, generate_lti_request


class LTITemplateTags(TestCase):

    def test_lti_session(self):
        with self.settings(PYLTI_CONFIG={'consumers': CONSUMERS}):
            request = generate_lti_request()
            self.assertIsNone(lti_session(request))

            # initialize the session
            lti = LTI('initial', 'any')
            self.assertTrue(lti.verify(request))

            lti = lti_session(request)
            self.assertEqual(lti.user_id(request), 'student')
