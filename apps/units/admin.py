from django.contrib import admin

from reversion.admin import VersionAdmin

from .models import Unit


class UnitAdmin(VersionAdmin):
    """
    Register django-revisions for a model
    """
    pass

admin.site.register(Unit, UnitAdmin)
