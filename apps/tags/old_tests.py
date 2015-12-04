import json

from django.utils import lorem_ipsum
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _

from .documents import Tag
from .factories import TagFactory
from common.testcase import BaseTestCase
from labs.factories import LabFactory
from profiles.factories import UserFactory


class TagTest(BaseTestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])

    def test_create(self):
        url = reverse('tags:create', kwargs={'lab_pk': self.lab.pk})
        data = {
            'details': lorem_ipsum.words(5),
            'params': json.dumps(dict(zip(range(0, 5), range(5, 10))))
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 1)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertContains(resp, 'Must be unique inside lab and parent', 1)

        data = {
            'details': lorem_ipsum.words(1, common=False),
            'params': json.dumps(dict(zip(range(0, 5), range(5, 10))))
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 2)

        data = {
            'details': lorem_ipsum.words(1, common=False),
            'params': json.dumps(dict(zip(range(0, 5), range(5, 10))))
        }
        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 3)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_update(self):
        material1 = TagFactory(lab=self.lab)
        url = reverse('tags:update', kwargs={'lab_pk': self.lab.pk, 'pk': material1.pk})
        data = {
            'details': lorem_ipsum.words(5),
            'params': json.dumps(dict(zip(range(0, 5), range(5, 10))))
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.get(pk=material1.pk).details, data['details'])

        self.client.login(username=self.member.email, password='qwerty')
        data.update({
            'details': lorem_ipsum.words(5),
            'params': json.dumps(dict(zip(range(0, 5), range(5, 10))))
        })
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.get(pk=material1.pk).details, data['details'])

        self.client.login(username=self.guest.email, password='qwerty')
        data.update({
            'details': lorem_ipsum.words(5),
            'params': json.dumps(dict(zip(range(0, 5), range(5, 10))))
        })
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.get(pk=material1.pk).details, data['details'])

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_delete(self):
        material = TagFactory(lab=self.lab)
        data = {'ids[]': [unicode(material.pk)]}
        url = reverse('tags:delete', kwargs={'lab_pk': self.lab.pk})
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        data = {'ids[]': [unicode(material.pk)]}
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 0)

        self.client.login(username=self.member.email, password='qwerty')
        material = TagFactory(lab=self.lab)
        data = {'ids[]': [unicode(material.pk)]}
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 0)

        self.client.login(username=self.guest.email, password='qwerty')
        material = TagFactory(lab=self.lab)
        data = {'ids[]': [unicode(material.pk)]}
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Tag.objects.count(), 0)

        self.client.login(username=self.user4.email, password='qwerty')
        material = TagFactory(lab=self.lab)
        data = {'ids[]': [unicode(material.pk)]}
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Tag.objects.count(), 1)
