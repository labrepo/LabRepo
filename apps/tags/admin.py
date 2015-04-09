from mongoadmin import site
from .documents import Tag
from common.admin import DocumentAdmin
from tags.forms import TagAdminForm


class TagAdmin(DocumentAdmin):
    list_display = ('lab', 'details')
    list_filter = ('lab', 'details')
    form = TagAdminForm


site.register(Tag, TagAdmin)
