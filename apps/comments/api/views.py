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
        return Comment.objects.filter(
            instance_type__model=self.kwargs.get('instance_type'),
            object_id=self.kwargs.get('object_id')
        ).order_by('action_time')

    def perform_create(self, serializer):
        obj = serializer.save()

        if obj.instance_type.name.lower() == 'experiment':
            experiment = obj.content_object
        else:
            experiment = None

        self.save_recent_activity(RecentActivity.COMMENT,
                                  value=obj.text,
                                  obj=obj.content_object,
                                  experiment=experiment)

        # # publish the message in the redis queue if it's experiment's comment
        if experiment:
            r = redis.StrictRedis(host='localhost', port=6379, db=3)
            channel = '{}'.format(obj.object_id)
            r.publish(channel, json.dumps({
                'comment': serializer.data,
            }))


class CommentDetailView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
