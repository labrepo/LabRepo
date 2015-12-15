from django.test import TestCase
from django.utils import lorem_ipsum
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _

from labs.models import Lab
from labs.factories import LabFactory
from profiles.models import LabUser
from profiles.factories import UserFactory
from tags.models import Tag
from tags.factories import TagFactory
from units.models import Unit
from units.factories import UnitFactory
from experiments.models import Experiment
from experiments.factories import ExperimentFactory


class TestLabTest(TestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()

    def test_create_lab(self):
        url = reverse('labs:create')
        name = lorem_ipsum.words(1, False)
        data = {
            'name': name,
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
        self.assertEqual(Lab.objects.all().first().name, name)

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

    def test_detail_all_member(self):
        lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        experiment = ExperimentFactory(lab=lab, owners=[self.owner.pk])

        url = reverse('labs:detail', kwargs={'lab_pk': lab.pk})
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, lab.name, 4)
        self.assertContains(resp, experiment.title, 3)  # TODO: third is commented

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, experiment.title, 3)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, experiment.title)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_detail_not_member(self):
        lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk])
        url = reverse('labs:detail', kwargs={'lab_pk': lab.pk})

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_create_test_lab(self):
        return True
        lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk], is_test=True)
        experiment1 = ExperimentFactory(lab=lab, owners=[self.owner.pk], editors=[self.guest.pk])
        experiment2 = ExperimentFactory(lab=lab, owners=[self.guest.pk], editors=[self.owner.pk])
        experiment3 = ExperimentFactory(lab=lab, owners=[self.member.pk], editors=[self.owner.pk])
        tag1 = TagFactory(lab=lab)
        tag2 = TagFactory(lab=lab, parent=tag1)
        tag3 = TagFactory(lab=lab, parent=tag2)
        tag4 = TagFactory.create_batch(10, lab=lab)
        tag5 = TagFactory.create_batch(5, lab=lab, parent=tag3)
        tag6 = TagFactory.create_batch(4, lab=lab, parent=tag2)
        TagFactory.create_batch(2, lab=lab, parent=tag2)
        UnitFactory(lab=lab, experiments=[experiment1,experiment2, experiment3], user=self.owner)
        UnitFactory(lab=lab, experiments=[experiment2], user=self.guest, tag=tag4+tag5+[tag3]+[tag2]+[tag1])
        UnitFactory(lab=lab, experiments=[experiment3], user=self.member, tag=tag4+tag6+[tag2]+[tag1])

        url = reverse('labs:create_test_lab')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        new_lab = Lab.objects.get(is_test=False)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Lab.objects.count(), 2)
        self.assertEqual(Unit.objects.filter(lab=new_lab).count(), 3)
        self.assertEqual(Tag.objects.filter(lab=new_lab).count(), 27)
        self.assertEqual(Experiment.objects.filter(lab=new_lab).count(), 3)
        self.assertEqual(Unit.objects.filter(lab=new_lab, experiments__in=Experiment.objects.filter(lab=new_lab)).count(), 3)
        for unit in Unit.objects.filter(lab=new_lab):
            self.assertIsNotNone(unit.measurements, True)

        parent_tag1 = Tag.objects.filter(lab=new_lab, parent=None)
        self.assertEqual(parent_tag1.count(), 14)
        parent_tag2 = Tag.objects.filter(lab=new_lab, parent__in=parent_tag1)
        self.assertEqual(parent_tag2.count(), 1)
        parent_tag3 = Tag.objects.filter(lab=new_lab, parent__in=parent_tag2)
        self.assertEqual(parent_tag3.count(), 7)

        self.assertEqual(Unit.objects.filter(lab=lab).count(), 3)
        self.assertEqual(Tag.objects.filter(lab=lab).count(), 27)
        self.assertEqual(Experiment.objects.filter(lab=lab).count(), 3)
        self.assertEqual(Unit.objects.filter(lab=lab, experiments__in=Experiment.objects.filter(lab=lab)).count(), 3)
        for unit in Unit.objects.filter(lab=lab):
            self.assertIsNotNone(unit.measurements, True)

        parent_tag1 = Tag.objects.filter(lab=lab, parent=None)
        self.assertEqual(parent_tag1.count(), 14)
        parent_tag2 = Tag.objects.filter(lab=lab, parent__in=parent_tag1)
        self.assertEqual(parent_tag2.count(), 1)
        parent_tag3 = Tag.objects.filter(lab=lab, parent__in=parent_tag2)
        self.assertEqual(parent_tag3.count(), 7)

    def test_change_investigator_by_member(self):
        """
        Check member can't change investigator in lab
        """
        lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk])
        url = reverse('labs:update', kwargs={'lab_pk': lab.pk})
        data = {
            'name': lorem_ipsum.words(1, False),
            'investigator': [self.member.pk],
            'members': [self.owner.pk],
            'guests': [self.guest.pk]
        }
        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'You have not permission change lab&#39;s investigator', 1)
        self.assertEqual(list(Lab.objects.first().investigator.all()), [self.owner])