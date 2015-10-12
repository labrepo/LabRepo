from django.contrib.webdesign import lorem_ipsum
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _

from mongoengine.django.auth import User
from labs.documents import Lab
from labs.factories import LabFactory
from common.testcase import BaseTestCase
from profiles.factories import UserFactory
from profiles.factories import UserFactory
from tags.documents import Tag
from tags.factories import TagFactory
from units.documents import Unit
from units.factories import UnitFactory
from experiments.documents import Experiment
from experiments.factories import ExperimentFactory


class TestLabTest(BaseTestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()

    def test_create_lab(self):
        url = reverse('labs:create')
        data = {
            'name': lorem_ipsum.words(1, False),
            'investigator': [self.owner.pk],
            'members': [self.member.pk],
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Lab.objects.count(), 1)

    def test_not_valid(self):
        url = reverse('labs:create')
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, {}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Lab.objects.count(), 0)
        self.assertContains(resp, _('This field is required'), 2)

    def test_update_lab(self):
        data = {
            'name': lorem_ipsum.words(1, False),
            'investigator': [self.owner.pk],
            'members': [self.member.pk],
            'guests': [self.guest.pk]
        }
        lab = LabFactory(**data)

        url = reverse('labs:update', kwargs={'lab_pk': lab.pk})
        data['name'] = name = 'test'
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Lab.objects.count(), 1)
        self.assertEqual(Lab.objects.first().name, name)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_delete_lab(self):
        lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        url = reverse('labs:delete', kwargs={'lab_pk': lab.pk})
        resp = self.client.post(url, {}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, {}, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Lab.objects.count(), 0)

        lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        url = reverse('labs:delete', kwargs={'lab_pk': lab.pk})
        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, {}, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, {}, follow=True)
        self.assertEqual(resp.status_code, 403)
