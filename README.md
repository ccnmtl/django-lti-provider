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

The ``LTI_TOOL_CONFIGURATION`` variable in your ``settings.py`` allows you to
configure your application's config.xml and set other options for the library. ([Edu Apps](https://www.edu-apps.org/code.html) has good documentation
on configuring an lti provider through xml.)
```
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
    'assignments': {
        '<name>': '<landing_url>',
        '<name>': '<landing_url>',
        '<name>': '<landing_url>'
    }
}
```

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

## Assignments

To support multiple assignments: 
* Create multiple endpoint views
* Add the assignment urls to the `LTI_TOOL_CONFIGURATION['assignments'] map
* Add an assignment, using the External Tool option.
   * Canvas: https://community.canvaslms.com/docs/DOC-10384-4152501360
* Update the URL to be `https://<your domain name>/lti/assignment/<assignment_name>`
* The `assignment_name` variable should match a landing_url in the LTI_TOOL_CONFIGURATION dict.
* Full example here: [Django LTI Provider Example](https://github.com/ccnmtl/django-lti-provider-example).
