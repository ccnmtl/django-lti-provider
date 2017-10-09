from django.contrib import admin
from lti_provider.models import LTICourseContext


@admin.register(LTICourseContext)
class AssetAdmin(admin.ModelAdmin):
    class Meta:
        model = LTICourseContext

    list_display = ('group', 'faculty_group')
