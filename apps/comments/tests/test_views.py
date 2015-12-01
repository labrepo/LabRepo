from django.contrib.webdesign import lorem_ipsum
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.test import TestCase

from comments.models import Comment
from comments.factories import CommentFactory
from common.testcase import BaseTestCase
from dashboard.models import RecentActivity
from experiments.factories import ExperimentFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory


class CommentTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])

    def test_create(self):
        url = reverse('comment:comment', kwargs={'lab_pk': self.lab.pk})
        data = {
            'create-text': lorem_ipsum.words(2),
            'create-instance_type': 'Experiment',
            'create-object_id': unicode(self.experiment.pk)
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)
        # self.assertEqual(RecentActivity.objects.all()[0].action_flag, RecentActivity.COMMENT)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.objects.count(), 2)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.objects.count(), 3)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_update(self):
        # comment = CommentFactory(object_id=self.experiment.id, init_user=self.guest, lab=self.lab)
        comment = CommentFactory(object_id=self.experiment.id, init_user=self.guest)
        url = reverse('comment:update', kwargs={'lab_pk': self.lab.pk, 'pk': unicode(comment.pk)})
        data = {
            'update-text': lorem_ipsum.words(2),
            'update-instance_type': 'Experiment',
            'update-object_id': unicode(self.experiment.pk)
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get(pk=comment.pk).text, data['update-text'])

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_delete(self):
        comment = CommentFactory(object_id=self.experiment.id, init_user=self.guest)
        url = reverse('comment:delete', kwargs={'lab_pk': self.lab.pk, 'pk': unicode(comment.pk)})
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.objects.count(), 0)

        comment = CommentFactory(object_id=self.experiment.id, init_user=self.guest)
        url = reverse('comment:delete', kwargs={'lab_pk': self.lab.pk, 'pk': unicode(comment.pk)})
        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Comment.objects.count(), 0)
