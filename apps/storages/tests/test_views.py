from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.test import TestCase

from labs.factories import LabFactory
from profiles.factories import UserFactory


class StoragesTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])

    def test_index_view(self):
        url = reverse('storages:index', kwargs={'lab_pk': self.lab.pk})

        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, u'Storage form')
