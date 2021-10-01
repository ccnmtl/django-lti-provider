from django.conf import settings
from django.contrib.auth import authenticate, login
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from lti_provider.lti import LTI
from lti_provider.models import LTICourseContext


class LTIAuthMixin(object):
    role_type = 'any'
    request_type = 'any'

    def join_groups(self, request, lti, ctx):
        # add the user to the requested groups
        request.user.groups.add(ctx.group)
        for role in lti.user_roles(request):
            role = role.lower()
            if ('staff' in role or
                'instructor' in role or
                    'administrator' in role):
                request.user.groups.add(ctx.faculty_group)
                break

            if settings.LTI_TOOL_CONFIGURATION.get('allow_ta_access', False):
                if 'teachingassistant' in role:
                    request.user.groups.add(ctx.faculty_group)
                    break

    def course_configuration(self, request, lti):
        # check if course is configured
        if settings.LTI_TOOL_CONFIGURATION['course_aware']:
            ctx = LTICourseContext.objects.get(
                lms_course_context=lti.course_context(request))

            # add user to the course
            self.join_groups(request, lti, ctx)

    def dispatch(self, request, *args, **kwargs):
        lti = LTI(self.request_type, self.role_type)

        # validate the user via oauth
        user = authenticate(request=request, lti=lti)
        if user is None:
            lti.clear_session(request)
            return HttpResponseRedirect(reverse('lti-fail-auth'))

        # login
        login(request, user)

        # configure course groups if requested
        try:
            self.course_configuration(request, lti)
        except (KeyError, ValueError, LTICourseContext.DoesNotExist):
            return HttpResponseRedirect(reverse('lti-course-config'))

        self.lti = lti
        return super(LTIAuthMixin, self).dispatch(request, *args, **kwargs)


class LTILoggedInMixin(object):
    role_type = 'any'
    request_type = 'any'

    def dispatch(self, request, *args, **kwargs):
        lti = LTI(self.request_type, self.role_type)

        # validate the user via oauth
        user = authenticate(request=request, lti=lti)
        if user is None:
            lti.clear_session(request)
            return HttpResponseRedirect(reverse('lti-fail-auth'))

        # login
        login(request, user)

        self.lti = lti
        return super(LTILoggedInMixin, self).dispatch(request, *args, **kwargs)
