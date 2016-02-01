from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from comments.models import Comment
from comments.models import Comment
from comments.factories import CommentFactory
from dashboard.models import RecentActivity
from experiments.factories import ExperimentFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory


class CommentApiListTests(APITestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        self.url = reverse('comment:api-list', kwargs={
            'lab_pk': self.lab.pk,
            'instance_type': 'experiment',
            'object_id': self.experiment.pk,
        })

    def test_get_view(self):

        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, 302)  # Login redirect

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        comment = CommentFactory(content_object=self.experiment, init_user=self.owner)
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, u'"instance_type":"experiment"')
        self.assertContains(resp, comment.text)

    def test_create_view(self):

        data = {
            'text': 'some text',
            'instance_type': 'experiment',
            'object_id': self.experiment.pk,
            'init_user': self.owner.pk
        }
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().text, 'some text')


class CommentApiDetailTests(APITestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        self.comment = CommentFactory(content_object=self.experiment, init_user=self.owner)
        self.url = reverse('comment:api-detail', kwargs={
            'lab_pk': self.lab.pk,
            'instance_type': 'experiment',
            'object_id': self.experiment.pk,
            'pk': self.comment.pk,
        })

    def test_get_view(self):

        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, 302)  # Login redirect

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, u'"instance_type":"experiment"')
        self.assertContains(resp, self.comment.text)

    def test_update_view(self):

        data = {
            'text': 'new text',
            'instance_type': 'experiment',
            'object_id': self.experiment.pk,
            'init_user': self.owner.pk,
        }
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.put(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().text, 'new text')

    def test_delete_view(self):

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.delete(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)


# TODO: another user