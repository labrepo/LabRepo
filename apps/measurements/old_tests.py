import json
import random
import datetime

from django.utils import lorem_ipsum
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _

from common.testcase import BaseTestCase
from experiments.factories import ExperimentFactory
from labs.factories import LabFactory
from measurements.documents import Measurement
from measurements.factories import MeasurementTypeFactory
from profiles.factories import UserFactory
from units.documents import Unit
from units.factories import UnitFactory


class MeasurementTest(BaseTestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        self.unit = UnitFactory(lab=self.lab, experiments=[self.experiment], user=self.owner)
        self.measurement_type = MeasurementTypeFactory(lab=self.lab)

    def test_create(self):
        self.unit.measurements = []
        self.unit.save(user=self.owner)
        url = reverse('measurements:create', kwargs={'unit_pk': self.unit.pk, 'lab_pk': self.lab.pk})
        data = {
            'data-0-created_at': datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
            'data-0-measurement_tpe <a href="#" class="btn btn-default append" data-toggle="modal" data-target="#modal" '
            'data-url="/53b29e8ab4abd0703756d081/measurements/measurement_type/append/" data-column="2">+</a>': self.measurement_type.__unicode__(),
            'data-0-unit type': lorem_ipsum.words(1, False),
            'data-0-value': random.random(),
            'data-0-measurement_type_pk': unicode(self.measurement_type.pk),

            'data-1-created_at': datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
            'data-1-measurement_tpe <a href="#" class="btn btn-default append" data-toggle="modal" data-target="#modal" '
            'data-url="/53b29e8ab4abd0703756d081/measurements/measurement_type/append/" data-column="2">+</a>': self.measurement_type.__unicode__(),
            'data-1-unit type': lorem_ipsum.words(1, False),
            'data-1-value': random.random(),
            'data-1-measurement_type_pk': unicode(self.measurement_type.pk),

            'data-2-created_at': datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
            'data-2-measurement_tpe <a href="#" class="btn btn-default append" data-toggle="modal" data-target="#modal" '
            'data-url="/53b29e8ab4abd0703756d081/measurements/measurement_type/append/" data-column="2">+</a>': self.measurement_type.__unicode__(),
            'data-2-unit type': lorem_ipsum.words(1, False),
            'data-2-value': random.random(),
            'data-2-measurement_type_pk': unicode(self.measurement_type.pk),
            'length': 3
        }

        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(Unit.objects.get(pk=self.unit.pk).measurements), 3)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(Unit.objects.get(pk=self.unit.pk).measurements), 6)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(len(Unit.objects.get(pk=self.unit.pk).measurements), 6)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(len(Unit.objects.get(pk=self.unit.pk).measurements), 6)

    def test_create_not_valid(self):
        url = reverse('measurements:create', kwargs={'unit_pk': self.unit.pk, 'lab_pk': self.lab.pk})
        data = {
            'data-0-measurement_tpe <a href="#" class="btn btn-default append" data-toggle="modal" data-target="#modal" '
            'data-url="/53b29e8ab4abd0703756d081/measurements/measurement_type/append/" data-column="2">+</a>': self.measurement_type.__unicode__(),
            'data-0-unit type': lorem_ipsum.words(1, False),
            'data-0-value': random.random(),
            'data-0-measurement_type_pk': unicode(self.measurement_type.pk),
            'length': 2
        }
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, json.dumps([[0, {"errors": {"created_at": ["This field is required."]}, "success": False}]]))

    def test_update(self):
        measurement = self.unit.measurements[0]
        url = reverse('measurements:create', kwargs={'unit_pk': self.unit.pk, 'lab_pk': self.lab.pk})
        data = {
            'data-0-pk': unicode(measurement.pk),
            'data-0-created_at': datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
            'data-0-measurement_type <a href="#" class="btn btn-default append" data-toggle="modal" data-target="#modal" '
            'data-url="/53b29e8ab4abd0703756d081/measurements/measurement_type/append/" data-column="2">+</a>': self.measurement_type.__unicode__(),
            'data-0-value': round(random.random(), 3),
            'data-0-measurement_type_pk': unicode(self.measurement_type.pk),
            'length': 2
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        measurement = Measurement.objects.get(pk=measurement.pk)
        print resp
        self.assertEqual(measurement.value, data['data-0-value'])

        self.client.login(username=self.member.email, password='qwerty')
        data['data-0-value'] = round(random.random(), 3)
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        measurement = Measurement.objects.get(pk=measurement.pk)
        self.assertEqual(measurement.value, data['data-0-value'])

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_update_description(self):
        measurement = self.unit.measurements[0]
        url = reverse('measurements:detail', kwargs={'pk': measurement.pk, 'unit_pk': self.unit.pk, 'lab_pk': self.lab.pk})
        data = {
            'description': lorem_ipsum.words(1, False)
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        measurement = Measurement.objects.get(pk=measurement.pk)
        self.assertEqual(measurement.description, data['description'])

        self.client.login(username=self.member.email, password='qwerty')
        data['description'] = lorem_ipsum.words(1, False)
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        measurement = Measurement.objects.get(pk=measurement.pk)
        self.assertEqual(measurement.description, data['description'])

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_delete(self):
        measurement = self.unit.measurements[0]
        url = reverse('measurements:delete', kwargs={'unit_pk': self.unit.pk, 'lab_pk': self.lab.pk})
        data = {'data': [unicode(measurement.pk)]}

        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Measurement.objects.count(), 2)
        self.assertFalse(Measurement.objects.get(pk=measurement.pk).active)

    def test_detail(self):
        measurement = self.unit.measurements[0]
        url = reverse('measurements:detail', kwargs={'unit_pk': self.unit.pk, 'lab_pk': self.lab.pk, 'pk': measurement.pk})

        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, measurement.description, 2)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)


class MeasurementTypeTest(BaseTestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        self.unit = UnitFactory(lab=self.lab, experiments=[self.experiment], user=self.owner)
        self.measurement_type = MeasurementTypeFactory(lab=self.lab)

    def test_create(self):
        pass
