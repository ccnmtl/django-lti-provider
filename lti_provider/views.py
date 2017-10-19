import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from lti_provider.lti import LTI
from lti_provider.models import LTICourseContext
from pylti.common import \
    generate_request_xml, LTIPostMessageException, post_message


class LTIAuthMixin(object):
    role_type = 'any'
    request_type = 'any'

    def join_groups(self, request, lti, ctx, user):
        # add the user to the requested groups
        user.groups.add(ctx.group)
        for role in lti.user_roles(request):
            role = role.lower()
            if ('staff' in role or
                'instructor' in role or
                    'administrator' in role):
                user.groups.add(ctx.faculty_group)
                break

    def dispatch(self, request, *args, **kwargs):
        lti = LTI(self.request_type, self.role_type)

        # validate the user via oauth
        user = authenticate(request=request, lti=lti)
        if user is None:
            lti.clear_session(request)
            return render(request, 'lti_provider/fail_auth.html', {})

        # login
        login(request, user)

        # check if course is configured
        if settings.LTI_TOOL_CONFIGURATION['course_aware']:
            try:
                ctx = LTICourseContext.objects.get(
                    lms_course_context=lti.course_context(request))
            except (KeyError, ValueError, LTICourseContext.DoesNotExist):
                return render(
                    request,
                    'lti_provider/fail_course_configuration.html',
                    {
                        'is_instructor': lti.is_instructor(request),
                        'is_administrator': lti.is_administrator(request),
                        'user': user,
                        'lms_course': lti.course_context(request),
                        'lms_course_title': lti.course_title(request),
                        'sis_course_id': lti.sis_course_id(request),
                        'domain': lti.canvas_domain(request)
                    })

            # add user to the course
            self.join_groups(request, lti, ctx, user)

        self.lti = lti
        return super(LTIAuthMixin, self).dispatch(request, *args, **kwargs)


class LTIRoutingView(LTIAuthMixin, View):
    request_type = 'initial'
    role_type = 'any'

    def add_extra_parameters(self, url):
        if not hasattr(settings, 'LTI_EXTRA_PARAMETERS'):
            return url

        if '?' not in url:
            url += '?'
        else:
            url += '&'

        for key in settings.LTI_EXTRA_PARAMETERS:
            url += '{}={}&'.format(key, self.request.POST.get(key, ''))

        return url

    def post(self, request):
        if request.POST.get('ext_content_intended_use', '') == 'embed':
            domain = self.request.get_host()
            url = '%s://%s/%s?return_url=%s' % (
                self.request.scheme, domain,
                settings.LTI_TOOL_CONFIGURATION['embed_url'],
                request.POST.get('launch_presentation_return_url'))
        elif settings.LTI_TOOL_CONFIGURATION['new_tab']:
            url = reverse('lti-landing-page',
                          args=[self.lti.course_context(request)])
        else:
            url = settings.LTI_TOOL_CONFIGURATION['landing_url'].format(
                self.request.scheme, self.request.get_host(),
                self.lti.course_context(request))

        url = self.add_extra_parameters(url)
        return HttpResponseRedirect(url)


class LTIConfigView(TemplateView):
    template_name = 'lti_provider/config.xml'
    content_type = 'text/xml; charset=utf-8'

    def get_context_data(self, **kwargs):
        domain = self.request.get_host()
        launch_url = '%s://%s/%s' % (
            self.request.scheme, domain,
            settings.LTI_TOOL_CONFIGURATION['launch_url'])

        ctx = {
            'domain': domain,
            'launch_url': launch_url,
            'title': settings.LTI_TOOL_CONFIGURATION['title'],
            'description': settings.LTI_TOOL_CONFIGURATION['description'],
            'embed_icon_url':
                settings.LTI_TOOL_CONFIGURATION['embed_icon_url'],
            'embed_tool_id': settings.LTI_TOOL_CONFIGURATION['embed_tool_id'],
            'frame_width': settings.LTI_TOOL_CONFIGURATION['frame_width'],
            'frame_height': settings.LTI_TOOL_CONFIGURATION['frame_height'],
        }
        return ctx


class LTILandingPage(TemplateView):
    template_name = 'lti_provider/landing_page.html'

    def get_context_data(self, **kwargs):
        domain = self.request.get_host()
        url = settings.LTI_TOOL_CONFIGURATION['landing_url'].format(
            self.request.scheme, domain, kwargs.get('context'))

        return {
            'landing_url': url,
            'title': settings.LTI_TOOL_CONFIGURATION['title']
        }


class LTICourseEnableView(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(self.__class__, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        group_id = self.request.POST.get('group')
        faculty_group_id = self.request.POST.get('faculty_group')
        course_context = self.request.POST.get('lms_course')
        title = self.request.POST.get('lms_course_title')

        (ctx, created) = LTICourseContext.objects.get_or_create(
            group=get_object_or_404(Group, id=group_id),
            faculty_group=get_object_or_404(Group, id=faculty_group_id),
            lms_course_context=course_context)

        messages.add_message(
            self.request, messages.INFO,
            '<strong>Success!</strong> {} is connected to {}.'.format(
                title, settings.LTI_TOOL_CONFIGURATION['title']))

        url = reverse('lti-landing-page', args=[course_context])
        return HttpResponseRedirect(url)


class LTIPostGrade(LTIAuthMixin, View):

    def message_identifier(self):
        return '{:.0f}'.format(time.time())

    def post(self, request, *args, **kwargs):
        """
        Post grade to LTI consumer using XML

        :param: grade: 0 <= grade <= 1
        :return: True is post successful and grade valid
        :exception: LTIPostMessageException if call failed
        """
        score = float(request.POST.get('score'))

        xml = generate_request_xml(
            self.message_identifier(), 'replaceResult',
            self.lti.lis_result_sourcedid(request), score)

        if not post_message(
            self.lti.consumers(), self.lti.oauth_consumer_key(request),
                self.lti.lis_outcome_service_url(request), xml):

            # Something went wrong, display an error.
            # Is 505 the right thing to do here?
            raise LTIPostMessageException('Post grade failed')
        else:
            redirect_url = request.POST.get('next', '/')
            return HttpResponseRedirect(redirect_url)
