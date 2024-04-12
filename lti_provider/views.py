import time
import os
import pprint

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls.exceptions import NoReverseMatch
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView
from lti_provider.mixins import LTIAuthMixin, LTILoggedInMixin
from lti_provider.models import LTICourseContext
from pylti.common import LTIPostMessageException, post_message

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.urls import reverse
from pylti1p3.contrib.django import (
    DjangoOIDCLogin, DjangoMessageLaunch, DjangoCacheDataStorage
)
from pylti1p3.deep_link_resource import DeepLinkResource
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.registration import Registration


class LTIConfigView(TemplateView):
    template_name = 'lti_provider/config.xml'
    content_type = 'text/xml; charset=utf-8'

    def get_context_data(self, **kwargs):
        domain = self.request.get_host()
        launch_url = '%s://%s/%s' % (
            self.request.scheme, domain,
            settings.LTI_TOOL_CONFIGURATION.get('launch_url'))

        ctx = {
            'domain': domain,
            'launch_url': launch_url,
            'title': settings.LTI_TOOL_CONFIGURATION.get('title'),
            'description': settings.LTI_TOOL_CONFIGURATION.get('description'),
            'embed_icon_url':
                settings.LTI_TOOL_CONFIGURATION.get('embed_icon_url'),
            'embed_tool_id': settings.LTI_TOOL_CONFIGURATION.get(
                'embed_tool_id'),
            'frame_width': settings.LTI_TOOL_CONFIGURATION.get('frame_width'),
            'frame_height': settings.LTI_TOOL_CONFIGURATION.get(
                'frame_height'),
            'course_navigation': settings.LTI_TOOL_CONFIGURATION.get(
                'course_navigation'),
            'custom_fields': settings.LTI_TOOL_CONFIGURATION.get(
                'custom_fields')
        }
        return ctx


@method_decorator(xframe_options_exempt, name='dispatch')
class LTIRoutingView(LTIAuthMixin, View):
    request_type = 'initial'
    role_type = 'any'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(LTIRoutingView, self).dispatch(*args, **kwargs)

    def add_custom_parameters(self, url):
        if not hasattr(settings, 'LTI_EXTRA_PARAMETERS'):
            return url

        if '?' not in url:
            url += '?'
        else:
            url += '&'

        for key in settings.LTI_EXTRA_PARAMETERS:
            url += '{}={}&'.format(key, self.request.POST.get(key, ''))

        return url

    def lookup_assignment_name(self, assignment_name, pk):
        try:
            # first see if there is a matching named view
            url = reverse(assignment_name, kwargs={'pk': pk})
        except NoReverseMatch:
            # otherwise look it up.
            assignments = settings.LTI_TOOL_CONFIGURATION['assignments']
            url = assignments[assignment_name]

        return url

    def post(self, request, assignment_name=None, pk=None):
        if request.POST.get('ext_content_intended_use', '') == 'embed':
            domain = self.request.get_host()
            url = '%s://%s/%s?return_url=%s' % (
                self.request.scheme, domain,
                settings.LTI_TOOL_CONFIGURATION.get('embed_url'),
                request.POST.get('launch_presentation_return_url'))
        elif assignment_name:
            url = self.lookup_assignment_name(assignment_name, pk)
        elif request.GET.get('assignment', None) is not None:
            assignment_name = request.GET.get('assignment')
            pk = request.GET.get('pk')
            url = self.lookup_assignment_name(assignment_name, pk)
        elif settings.LTI_TOOL_CONFIGURATION.get('new_tab'):
            url = reverse('lti-landing-page')
        else:
            url = settings.LTI_TOOL_CONFIGURATION['landing_url'].format(
                self.request.scheme, self.request.get_host())

        # custom parameters can be tacked on here
        url = self.add_custom_parameters(url)

        return HttpResponseRedirect(url)


@method_decorator(xframe_options_exempt, name='dispatch')
class LTILandingPage(LTIAuthMixin, TemplateView):
    template_name = 'lti_provider/landing_page.html'

    def get_context_data(self, **kwargs):
        domain = self.request.get_host()
        url = settings.LTI_TOOL_CONFIGURATION['landing_url'].format(
            self.request.scheme, domain, self.lti.course_context(self.request))
        is_auth_ta = None
        if settings.LTI_TOOL_CONFIGURATION.get('allow_ta_access', False):
            role = self.request.session.get('roles', '').lower()
            is_auth_ta = 'teachingassistant' in role

        return {
            'landing_url': url,
            'title': settings.LTI_TOOL_CONFIGURATION.get('title'),
            'is_instructor': self.lti.is_instructor(self.request),
            'is_administrator': self.lti.is_administrator(self.request),
            'is_auth_ta': is_auth_ta
        }


@method_decorator(xframe_options_exempt, name='dispatch')
class LTIFailAuthorization(TemplateView):
    template_name = 'lti_provider/fail_auth.html'


@method_decorator(xframe_options_exempt, name='dispatch')
class LTICourseConfigure(LTILoggedInMixin, TemplateView):
    template_name = 'lti_provider/fail_course_configuration.html'

    def get_context_data(self, **kwargs):
        return {
            'is_instructor': self.lti.is_instructor(self.request),
            'is_administrator': self.lti.is_administrator(self.request),
            'user': self.request.user,
            'lms_course': self.lti.course_context(self.request),
            'lms_course_title': self.lti.course_title(self.request),
            'sis_course_id': self.lti.sis_course_id(self.request),
            'domain': self.lti.canvas_domain(self.request)
        }


@method_decorator(xframe_options_exempt, name='dispatch')
class LTICourseEnableView(LTILoggedInMixin, View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(self.__class__, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        group_id = self.request.POST.get('group')
        faculty_group_id = self.request.POST.get('faculty_group')
        course_context = self.lti.course_context(self.request)
        title = self.lti.course_title(self.request)

        (ctx, created) = LTICourseContext.objects.get_or_create(
            group=get_object_or_404(Group, id=group_id),
            faculty_group=get_object_or_404(Group, id=faculty_group_id),
            lms_course_context=course_context)

        messages.add_message(
            self.request, messages.INFO,
            '<strong>Success!</strong> {} is connected to {}.'.format(
                title, settings.LTI_TOOL_CONFIGURATION.get('title')))

        url = reverse('lti-landing-page', args=[course_context])
        return HttpResponseRedirect(url)


class LTIPostGrade(LTIAuthMixin, View):

    def message_identifier(self):
        return '{:.0f}'.format(time.time())

    def post(self, request, *args, **kwargs):
        """
        Post grade to LTI consumer using XML

        :param: score: 0 <= score <= 1. (Score MUST be between 0 and 1)
        :return: True if post successful and score valid
        :exception: LTIPostMessageException if call failed
        """
        try:
            score = float(request.POST.get('score'))
        except ValueError:
            score = 0

        redirect_url = request.POST.get('next', '/')
        launch_url = request.POST.get('launch_url', None)

        xml = self.lti.generate_request_xml(
            self.message_identifier(), 'replaceResult',
            self.lti.lis_result_sourcedid(request), score, launch_url)

        if not post_message(
            self.lti.consumers(), self.lti.oauth_consumer_key(request),
                self.lti.lis_outcome_service_url(request), xml):

            msg = ('An error occurred while saving your score. '
                   'Please try again.')
            messages.add_message(request, messages.ERROR, msg)

            # Something went wrong, display an error.
            # Is 500 the right thing to do here?
            raise LTIPostMessageException('Post grade failed')
        else:
            msg = ('Your score was submitted. Great job!')
            messages.add_message(request, messages.INFO, msg)

            return HttpResponseRedirect(redirect_url)


#
# New pylti1p3 funtionality below, adapted from pylti1.3-django-example
#
#   https://github.com/dmitry-viskov/pylti1.3-django-example
#
class ExtendedDjangoMessageLaunch(DjangoMessageLaunch):

    def validate_nonce(self):
        """
        Probably it is bug on "https://lti-ri.imsglobal.org":
        site passes invalid "nonce" value during deep links launch.
        Because of this in case of iss == http://imsglobal.org just
        skip nonce validation.

        """
        iss = self.get_iss()
        deep_link_launch = self.is_deep_link_launch()
        if iss == "http://imsglobal.org" and deep_link_launch:
            return self
        return super().validate_nonce()


def get_lti_config_path():
    return os.path.join(settings.BASE_DIR, 'configs', 'config.json')


def get_tool_conf():
    tool_conf = ToolConfJsonFile(get_lti_config_path())
    return tool_conf


def get_jwk_from_public_key(key_name):
    key_path = os.path.join(settings.BASE_DIR, 'configs', key_name)
    f = open(key_path, 'r')
    key_content = f.read()
    jwk = Registration.get_jwk(key_content)
    f.close()
    return jwk


def get_launch_data_storage():
    return DjangoCacheDataStorage()


def get_launch_url(request) -> str:
    target_link_uri = request.POST.get(
        'target_link_uri', request.GET.get('target_link_uri'))

    # If this wasn't in the request, this shouldn't be too hard to
    # find. It's just the launch route.
    if not target_link_uri:
        target_link_uri = reverse('lti-launch')

    # If we really can't find this, then fail.
    if not target_link_uri:
        raise Exception('Missing "target_link_uri" param')

    return target_link_uri


def login(request):
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()

    oidc_login = DjangoOIDCLogin(
        request, tool_conf, launch_data_storage=launch_data_storage)
    target_link_uri = get_launch_url(request)
    return oidc_login\
        .enable_check_cookies()\
        .redirect(target_link_uri)


@require_POST
def launch(request):
    # TODO: make this course context aware - migrate functionality
    # from LTILandingPage.get_context_data.
    landing_url = settings.LTI_TOOL_CONFIGURATION['landing_url']

    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedDjangoMessageLaunch(
        request, tool_conf, launch_data_storage=launch_data_storage)
    message_launch_data = message_launch.get_launch_data()
    pprint.pprint(message_launch_data)

    return render(request, 'lti_provider/landing_page.html', {
        'landing_url': landing_url,
        'page_title': 'Page Title',
        'is_deep_link_launch': message_launch.is_deep_link_launch(),
        'launch_data': message_launch.get_launch_data(),
        'launch_id': message_launch.get_launch_id(),
        'curr_user_name': message_launch_data.get('name', ''),
    })


def get_jwks(request):
    tool_conf = get_tool_conf()
    return JsonResponse(tool_conf.get_jwks(), safe=False)


def configure(request, launch_id):
    tool_conf = get_tool_conf()
    launch_data_storage = get_launch_data_storage()
    message_launch = ExtendedDjangoMessageLaunch.from_cache(
        launch_id, request, tool_conf,
        launch_data_storage=launch_data_storage)

    if not message_launch.is_deep_link_launch():
        return HttpResponseForbidden('Must be a deep link!')

    launch_url = request.build_absolute_uri(reverse('lti-launch'))

    resource = DeepLinkResource()
    resource.set_url(launch_url).set_title('Custom title!')

    html = message_launch.get_deep_link().output_response_form([resource])
    return HttpResponse(html)
