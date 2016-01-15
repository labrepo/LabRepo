from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import Measurement


class MeasurementAdmin(VersionAdmin):
    """Register django-revisions for a measurement model"""
    pass

admin.site.register(Measurement, MeasurementAdmin)