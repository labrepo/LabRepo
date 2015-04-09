from django.views.generic import ListView, DetailView
from mongoreversion.models import ContentType

from common.mixins import LoginRequiredMixin, CheckViewPermissionMixin
from history.documents import History


class HistoryListView(LoginRequiredMixin, ListView):
    """
    View for display all history about object (unit or measurement).
    """
    model = History
    template_name = 'history/history_list.html'

    def get_queryset(self):
        try:
            instance_type = ContentType.objects.get(class_name__iexact=self.kwargs['class_name'])
            user = self.request.user
            queryset = self.model.objects.filter(instance_type=instance_type, instance_id=self.kwargs['pk']).order_by('-timestamp')
            # todo change
            exclude_pk = []
            for query in queryset:
                if not query.is_assistant(user):
                    exclude_pk.append(query.pk)
            return queryset.filter(pk__not__in=exclude_pk)
        except ContentType.DoesNotExist:
            return ContentType.objects.none()


class HistoryDetailView(LoginRequiredMixin, CheckViewPermissionMixin, DetailView):
    """
    View for display detailed information about object (unit or measurement), who and why was created or changed it.
    """
    model = History
    template_name = 'history/history_detail.html'