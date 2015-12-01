from django.test import TestCase
from django.contrib.webdesign import lorem_ipsum
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from experiments.models import Experiment
from experiments.factories import ExperimentFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory
from units.factories import UnitFactory


class ExperimentTest(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])

    def test_create(self):
        url = reverse('experiments:create', kwargs={'lab_pk': self.lab.pk})
        data = {
            'owners': [self.owner.pk],
            'start': timezone.now().strftime('%m/%d/%Y %H:%M'),
            'end': timezone.now().strftime('%m/%d/%Y %H:%M'),
            'description': lorem_ipsum.words(2),
            'title': lorem_ipsum.words(2),
            'status': Experiment.STATUS[0][0]
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Experiment.objects.count(), 1)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Experiment.objects.count(), 2)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Experiment.objects.count(), 3)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_create_not_valid(self):
        url = reverse('experiments:create', kwargs={'lab_pk': self.lab.pk})
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, {}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('This field is required'), 4)

    def test_update(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        url = reverse('experiments:update', kwargs={'lab_pk': self.lab.pk, 'pk': experiment.pk})
        data = {
            'owners': [self.owner.pk],
            'start': timezone.now().strftime('%m/%d/%Y %H:%M'),
            'end': timezone.now().strftime('%m/%d/%Y %H:%M'),
            'description': lorem_ipsum.words(2),
            'title': lorem_ipsum.words(2),
            'status': Experiment.STATUS[0][0]
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Experiment.objects.count(), 1)
        experiment = Experiment.objects.get(pk=experiment.pk)
        self.assertEqual(experiment.description, data['description'])

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_delete(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        url = reverse('experiments:delete', kwargs={'pk': experiment.pk, 'lab_pk': self.lab.pk})

        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Experiment.objects.count(), 1)
        self.assertFalse(Experiment.objects.get(pk=experiment.pk).active)

    def test_detail_with_owner(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        unit = UnitFactory(experiments=[experiment], lab=self.lab)
        url = reverse('experiments:detail', kwargs={'lab_pk': self.lab.pk, 'pk': experiment.pk})

        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, unit.get_absolute_url(), 1)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

    def tjest_detail_with_guest(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.guest.pk])
        unit = UnitFactory(experiments=[experiment], lab=self.lab, user=self.owner)
        url = reverse('experiments:detail', kwargs={'lab_pk': self.lab.pk, 'pk': experiment.pk})

        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, unit.get_absolute_url(), 1)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_change_owners_by_editor(self):
        """
        Check Editors can't change owners in experiments
        """
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.member.pk])
        url = reverse('experiments:update', kwargs={'lab_pk': self.lab.pk, 'pk': experiment.pk})
        data = {
            'owners': [self.member.pk],
            'editors': [self.owner.pk],
            'start': timezone.now().strftime('%m/%d/%Y %H:%M'),
            'end': timezone.now().strftime('%m/%d/%Y %H:%M '),
            'description': lorem_ipsum.words(2),
            'title': lorem_ipsum.words(2),
            'status': Experiment.STATUS[0][0]
        }
        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'You have not permission change owners', 1)
        self.assertEqual(list(Experiment.objects.all().first().owners.all()), [self.owner])
