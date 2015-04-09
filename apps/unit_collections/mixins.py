from common.mixins import CheckLabPermissionMixin, RecentActivityMixin, AjaxableResponseMixin, JsTreeMixin, \
    ActiveTabMixin, FormInitialMixin
from dashboard.documents import RecentActivity
from unit_collections.documents import Collection
from unit_collections.forms import CollectionForm


class CollectionPermissionMixin(CheckLabPermissionMixin, FormInitialMixin, AjaxableResponseMixin, RecentActivityMixin,
                                JsTreeMixin, ActiveTabMixin):
    model = Collection
    form_class = CollectionForm
    template_name = 'unit_collections/unit_collections_form.html'
    active_tab = 'collections'
    fields = ('id', 'title', 'title')
    parent_id = '#'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.lab = self.lab
        self.object.save()
        self.save_recent_activity(RecentActivity.ADD)
        return self.render_to_json_response({'message': self.get_success_message(),
                                             'node': self.get_jstree_data([self.object], self.fields, self.parent_id)})
