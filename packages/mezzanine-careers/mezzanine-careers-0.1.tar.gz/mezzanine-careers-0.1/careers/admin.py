
from copy import deepcopy

from django.contrib import admin

from careers.models import JobPost
from mezzanine.conf import settings
from mezzanine.core.admin import DisplayableAdmin


jobpost_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
jobpost_fieldsets[0][1]["fields"].extend(["content",])
jobpost_list_display = ["title", "status", "admin_link"]


class JobPostAdmin(DisplayableAdmin):
    """
    Admin class for job posts.
    """

    fieldsets = jobpost_fieldsets
    list_display = jobpost_list_display

    def save_form(self, request, form, change):
        return DisplayableAdmin.save_form(self, request, form, change)


admin.site.register(JobPost, JobPostAdmin)
