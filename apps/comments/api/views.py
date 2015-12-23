# -*- coding: utf-8 -*-
import json
import redis

from rest_framework import generics

from common.mixins import LoginRequiredMixin, CheckLabPermissionMixin, RecentActivityMixin
from dashboard.models import RecentActivity
from comments.api.serializers import CommentSerializer
from comments.models import Comment


class CommentListView(LoginRequiredMixin, CheckLabPermissionMixin, RecentActivityMixin, generics.ListCreateAPIView):

    serializer_class = CommentSerializer

    def get_queryset(self, **kwargs):
        return Comment.objects.filter(instance_type__model=self.kwargs.get('instance_type'), object_id=self.kwargs.get('object_id')).order_by('action_time')

    def perform_create(self, serializer):
        obj = serializer.save()
        if obj.instance_type.name.lower() == 'experiment':
            experiment = obj.content_object
        else:
            experiment = None
        resent_activity = self.save_recent_activity(RecentActivity.COMMENT,
                                                    value=obj.text,
                                                    obj=obj.content_object,
                                                    experiment=experiment)

        # # publish message in the redis queue if experiment's comment
        if experiment:
            r = redis.StrictRedis(host='localhost', port=6379, db=3)
            p = r.pubsub()
            channel = '{}'.format(obj.object_id)
            html = '123' #render_to_string(self.template_name, {'comment': self.object, 'lab': self.lab})
            r.publish(channel, json.dumps({
                'html': html,
                'comment': serializer.data,
                'user_pk': u'{}'.format(obj.init_user.pk),
            }))


class CommentDetailView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def get_object(self):
        return Comment.objects.get(id=self.kwargs.get('pk'))