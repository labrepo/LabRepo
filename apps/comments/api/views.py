# -*- coding: utf-8 -*-
import json
import redis

from rest_framework import generics

from common.mixins import LoginRequiredMixin, CheckLabPermissionMixin, RecentActivityMixin
from dashboard.models import RecentActivity
from .serializers import CommentSerializer
from ..models import Comment


class CommentListView(LoginRequiredMixin, CheckLabPermissionMixin, RecentActivityMixin, generics.ListCreateAPIView):

    serializer_class = CommentSerializer

    def get_queryset(self, **kwargs):
        return Comment.objects.filter(
            instance_type__model=self.kwargs.get('instance_type'),
            object_id=self.kwargs.get('object_id')
        ).order_by('action_time')

    def perform_create(self, serializer):
        """
        Create a comment instance, create recent activity record. Also, publish a message to Redis.
        """
        obj = serializer.save(init_user=self.request.user)

        if obj.instance_type.name.lower() == 'experiment':
            experiment = obj.content_object
        else:
            experiment = None

        self.save_recent_activity(RecentActivity.COMMENT,
                                  value=obj.text,
                                  obj=obj.content_object,
                                  experiment=experiment)

        # Publish a message in the redis queue if it's an experiment's comment
        if experiment:
            r = redis.StrictRedis(host='localhost', port=6379, db=3)
            channel = '{}'.format(obj.object_id)
            r.publish(channel, json.dumps({
                'comment': serializer.data,
            }))


class CommentDetailView(LoginRequiredMixin, CheckLabPermissionMixin, generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def perform_update(self, serializer):
        serializer.save(init_user=self.request.user)

