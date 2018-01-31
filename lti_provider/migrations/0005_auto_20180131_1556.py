# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lti_provider', '0004_lticoursecontext_enable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lticoursecontext',
            name='enable',
        ),
        migrations.RemoveField(
            model_name='lticoursecontext',
            name='uuid',
        ),
        migrations.AddField(
            model_name='lticoursecontext',
            name='lms_course_context',
            field=models.CharField(max_length=255, unique=True, null=True),
        ),
    ]
