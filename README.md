[![Actions Status](https://github.com/ccnmtl/django-lti-provider/workflows/build-and-test/badge.svg)](https://github.com/ccnmtl/django-lti-provider/actions)

# Documentation

django-lti-provider provides LTI functionality for the Django web framework. This
work began as a port of MIT's [LTI Flask Sample](https://github.com/mitodl/mit_lti_flask_sample),
which demonstrates a sample LTI provider for the Flask Framework based on
the [Python LTI library, PyLTI](https://github.com/mitodl/pylti).

Additional work was completed to provide fuller functionality and support the idiosyncrasies of various LMS systems
such as Canvas, Blackboard, Moodle and EdEx.

django-lti-provider offers:

* an authentication backend to complete an oAuth handshake (optional)
* a templated view for config.xml generation
* a templated landing page view for those LMS who do not have a 'launch in new tab' option, i.e. Canvas
* support for Canvas' [embedded tool extensions](https://canvas.instructure.com/doc/api/file.editor_button_tools.html)
* routing for multiple external assignment end points.

The library is used at Columbia University's [Center for Teaching And Learning](http://ctl.columbia.edu).

See an example Django app using the library at [Django LTI Provider Example](https://github.com/ccnmtl/django-lti-provider-example).

## Installation

You can install ```django-lti-provider``` through ```pip```:

```python
$ pip install django-lti-provider
```
Or, if you're using virtualenv, add ```django-lti-provider``` to your ```requirements.txt```.

Add to ```INSTALLED_APPS``` in your ```settings.py```::

```python
  'lti_provider',
```

## Dependencies

* Django
* nameparser
* httplib2
* oauth2
* oauthlib
* pylti

## Configuration

### Basic setup steps

Add the URL route::

```python
url(r'^lti/', include('lti_provider.urls'))

```

Add the LTIBackend to your AUTHENTICATION_BACKENDS:

```python
AUTHENTICATION_BACKENDS = [
  'django.contrib.auth.backends.ModelBackend',
  'lti_provider.auth.LTIBackend',
]
```

Complete a migration

```python
   ./manage.py migrate
```

### Primary LTI config

The ``LTI_TOOL_CONFIGURATION`` variable in your ``settings.py`` allows you to
configure your application's config.xml and set other options for the library. ([Edu Apps](https://www.edu-apps.org/code.html) has good documentation
on configuring an lti provider through xml.)

```python
LTI_TOOL_CONFIGURATION = {
    'title': '<your lti provider title>',
    'description': '<your description>',
    'launch_url': 'lti/',
    'embed_url': '<the view endpoint for an embed tool>' or '',
    'embed_icon_url': '<the icon url to use for an embed tool>' or '',
    'embed_tool_id': '<the embed tool id>' or '',
    'landing_url': '<the view landing page>',
    'course_aware': <True or False>,
    'course_navigation': <True or False>,
    'new_tab': <True or False>,
    'frame_width': <width in pixels>,
    'frame_height': <height in pixels>,
    'custom_fields': <dictionary>,
    'allow_ta_access': <True or False>,
    'assignments': {
        '<name>': '<landing_url>',
        '<name>': '<landing_url>',
        '<name>': '<landing_url>',
    },
}
```

To stash custom properties in your session, populate the `LTI_PROPERTY_LIST_EX` variable in your `settings.py`. This is useful for LMS specific `custom_x` parameters that will be needed later. The default value for `LTI_PROPERTY_LIST_EX` is: `['custom_canvas_user_login_id', 'context_title', 'lis_course_offering_sourcedid', 'custom_canvas_api_domain']`.

```python
LTI_PROPERTY_LIST_EX = ['custom_parameter1', 'custom_parameter2']
```

### Using a cookie based session

For simplest scenarios you can store data for the LTI request in a session cookie.
This is the quickest way to get up and running, and due to Django's tamper
proof cookie session (assuming a secure secret key) it is a safe option.
Please note that you will need to add the following settings in your
applications `settings.py` to make use of cookies:

```python
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = True
```

Because Canvas sends the information that we are storing in a `POST`
request on the LTI launch, we need to relax the restriction of cookies
only being allowed to be set from the same site. For more information on
`SESSION_COOKIE_SAMESITE` [read here](https://docs.djangoproject.com/en/3.0/ref/settings/#session-cookie-samesite).

For more information on why `SESSION_COOKIE_SAMESITE` and `SESSION_COOKIE_SECURE`
are needed, if you are choosing to make use of cookies, please read
[here.](https://community.canvaslms.com/t5/Developers-Group/SameSite-Cookies-and-Canvas/ba-p/257967)

### Extra LTI Configuration values

To specify a custom username property, add the `LTI_PROPERTY_USER_USERNAME` variable to your `settings.py`. By default, `LTI_PROPERTY_USER_USERNAME` is `custom_canvas_user_login_id`. This value can vary depending on your LMS.

To pass through extra LTI parameters to your provider, populate the `LTI_EXTRA_PARAMETERS` variable in your `settings.py`.
This is useful for custom parameters you may specify at installation time.

```python
LTI_EXTRA_PARAMETERS = ['lti_version']  # example
```

The ``PYLTI_CONFIG`` variable in your ``settings.py`` configures the
application consumers and secrets.

```python
PYLTI_CONFIG = {
    'consumers': {
        '<random number string>': {
            'secret': '<random number string>'
        }
    }
}
```

### Canvas and LTI iframes

Since LTI tools live within an iframe on Canvas, you **might** need
adjust your `X_FRAME_OPTIONS` setting to allow for the LTI tool to be
opened within the iframe. To the best of our knowledge you probably
don't have to adjust this setting, as Canvas has built a workaround.
For more info [read here](https://github.com/ccnmtl/django-lti-provider/issues/280)

This ensures that the Django application will allow requests from your
orgs Canvas instance. For more on `X_FRAME_OPTIONS` please
[consult here](https://docs.djangoproject.com/en/3.0/ref/clickjacking/#module-django.middleware.clickjacking).

### If you are using a load balancer

If you happen to have a deployment scenario where you have load balancer
listening on https and routing traffic to nodes that are listening to HTTP,
you will need to add the following line of configuration in `settings.py`:

```python
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

This ensures the correct `launch_url` is generated for the LTI tool.
For more on this setting, [read here](https://docs.djangoproject.com/en/3.1/ref/settings/#secure-proxy-ssl-header).

## Assignments

To support multiple assignments:

* Create multiple endpoint views
* Add the assignment urls to the `LTI_TOOL_CONFIGURATION['assignments'] map
* Add an assignment, using the External Tool option.
   * Canvas: https://community.canvaslms.com/docs/DOC-10384-4152501360
* Update the URL to be `https://<your domain name>/lti/assignment/<assignment_name>`
* The `assignment_name` variable should match a landing_url in the LTI_TOOL_CONFIGURATION dict.
* Full example here: [Django LTI Provider Example](https://github.com/ccnmtl/django-lti-provider-example).

OR

* Create a single named endpoint that accepts an id
* On Post, django-lti-provider will attempt to reverse the assignment_name/id and then redirect to that view.
