from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from reversion import revisions as reversion

from measurements.models import Measurement
from units.factories import UnitFactory
from experiments.factories import ExperimentFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory


class MeasurementApiTableTests(APITestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        self.unit = UnitFactory(lab=self.lab, experiments=[self.experiment])
        self.measurement = self.unit.measurement
        self.url = reverse('measurements:api-table', kwargs={
            'lab_pk': self.lab.pk,
            'pk': self.unit.pk,
        })

    def test_get_view(self):
        resp = self.client.get(self.url, format='json')
        self.assertNotEqual(resp.status_code, 200)

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(self.url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertContains(resp, '"table_data":[["",""]]')

    def test_update_view(self):

        data = {
            'headers': ["h1", "h2"],
            'table_data': [["a1", "a2"], ["b1", "b2"]]
        }
        resp = self.client.put(self.url, data, format='json')
        self.assertNotEqual(resp.status_code, 200)

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.put(self.url, data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        measurement = Measurement.objects.get(id=self.measurement.id)
        self.assertEqual(measurement.headers, data['headers'])
        self.assertEqual(measurement.table_data, data['table_data'])
        self.assertEqual(len(list(reversion.get_for_object(measurement))), 1)  # Check revisions


class MeasurementApiRevisionTests(APITestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        self.unit = UnitFactory(lab=self.lab, experiments=[self.experiment])
        self.measurement = self.unit.measurement
        self.updata_url = reverse('measurements:api-table', kwargs={
            'lab_pk': self.lab.pk,
            'pk': self.unit.pk,
        })

    def test_get_view(self):
        self.client.login(username=self.owner.email, password='qwerty')

        data = {
            'headers': ["h1", "h2"],
            'table_data': [["a1", "a2"], ["b1", "b2"]]
        }
        resp = self.client.put(self.updata_url, data, format='json')
        revision_id = resp.data['revisions'][0]['id']
        data2 = {
            'headers': ["h3", "h4"],
            'table_data': [["c1", "c2"], ["b1", "b2"]]
        }
        resp = self.client.put(self.updata_url, data, format='json')
        url = reverse('measurements:api-revision', kwargs={
            'lab_pk': self.lab.pk,
            'pk': self.unit.pk,
            'revision_pk': revision_id,
        })
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.data['headers'], data['headers'])
        self.assertEqual(resp.data['table_data'], data['table_data'])

        self.client.logout()
        resp = self.client.get(url, format='json')
        self.assertNotEqual(resp.status_code, 200)



