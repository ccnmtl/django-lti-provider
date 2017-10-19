Important: More documentation and examples to come. This is a work in progress as code is generalized from another application. This library is not yet on pypi, but will be soon.

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

The library is used at Columbia University's [Center for Teaching And Learning](http://ctl.columbia.edu) in [Mediathread](http://www.github.com/ccnmtl/mediathread).


## Installation

You can install ```django-lti-provider``` through ```pip```::
```python
$ pip install django-lti-provider
```
In your project, add ```django-lti-provider``` to your ```requirements.txt```.

Add to ```INSTALLED_APPS``` in your ```settings.py```::
```python
  'lti_provider',
```

## Dependencies

* Django
* nameparser
* httplib2
* oauth
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

```
The ``LTI_TOOL_CONFIGURATION`` variable in your ``settings.py`` allows you to
configure your application's config.xml. ([Edu Apps](https://www.edu-apps.org/code.html) has good documentation
on configuring an lti provider through xml.)
```
LTI_TOOL_CONFIGURATION = {
    'title': '<your lti provider title>',
    'description': '<your description>'
    'launch_url': 'lti/',
    'embed_url': '<the view endpoint for an embed tool>' or '',
    'embed_icon_url': '<the icon url to use for an embed tool>' or '',
    'embed_tool_id': '<the embed tool id>' or '',
    'landing_url': '<the view landing page>',
    'course_aware': '<True or False>',
    'course_navigation': '<True or False>',
    'assignment_new_tab': '<True or False>',
    'frame_width': <width in pixels>,
    'frame_height': <height in pixels>
}

To pass through extra LTI parameters to your provider, populate the LTI_EXTRA_PARAMETERS variable in your settings.py

LTI_EXTRA_PARAMETERS = ['lti_version']

The ``PYLTI_CONFIG`` variable in your ``settings.py`` configures the 
application consumers and secrets.

PYLTI_CONFIG = {
    'consumers': {
        '<random number string>': {
            'secret': '<random number string>'
        }
    }
}

## LMS Configuration

Now, add your application to your favorite LMS provider.
