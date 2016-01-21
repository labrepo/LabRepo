from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from storages.models import LabStorage
from storages.factories import StorageFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory


class StoragesApiListTests(APITestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.url = reverse('storages:api-list', kwargs={
            'lab_pk': self.lab.pk,
        })

    def test_get_view(self):

        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, 302)  # Login redirect

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        storage = StorageFactory(lab=self.lab)
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, storage.host)
        self.assertNotContains(resp, 'password')

    def test_create_view(self):
        data = {
            'type': 1,
            'username': "admin",
            'password': "password",
            'host': "localhost",
            'path': "/home/user1",
            'lab': self.lab.pk
        }
        self.client.login(username=self.owner.email, password='qwerty')

        resp = self.client.post(self.url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LabStorage.objects.count(), 1)
        self.assertEqual(LabStorage.objects.get().host, 'localhost')

        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, 'localhost')
        self.assertNotContains(resp, 'password')


class StoragesApiDetailTests(APITestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.storage = StorageFactory(lab=self.lab)
        self.url = reverse('storages:api-detail', kwargs={
            'lab_pk': self.lab.pk,
            'pk': self.storage.pk,
        })

    def test_get_view(self):

        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, 302)  # Login redirect

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, self.storage.host)
        self.assertNotContains(resp, self.storage.password)

    def test_update_view(self):

        data = {
            'host': "localhost2",
            'lab': self.storage.lab.pk,
            'type': self.storage.type,
            'username': self.storage.username,
        }
        self.client.login(username=self.owner.email, password='qwerty')

        resp = self.client.put(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(LabStorage.objects.count(), 1)
        self.assertEqual(LabStorage.objects.get().host, 'localhost2')

    def test_delete_view(self):

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.delete(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(LabStorage.objects.count(), 0)


# TODO: recent activity, another user