from django.contrib.auth.models import Group
from django.db import models


class LTICourseContext(models.Model):
    group = models.ForeignKey(Group,
                              related_name='course_group',
                              on_delete=models.CASCADE)
    faculty_group = models.ForeignKey(Group,
                                      related_name='course_faculty_group',
                                      on_delete=models.CASCADE)
    lms_course_context = models.CharField(null=True,
                                          unique=True,
                                          max_length=255)

    class Meta:
        unique_together = (('group', 'faculty_group'),)
