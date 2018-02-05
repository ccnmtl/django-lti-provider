# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lti_provider', '0005_auto_20171009_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lticoursecontext',
            name='lms_course_context',
            field=models.CharField(max_length=255, unique=True, null=True),
        ),
    ]
