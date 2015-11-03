import json
import random
from django.contrib.webdesign import lorem_ipsum

from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _

from common.testcase import BaseTestCase
from experiments.factories import ExperimentFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory
from tags.factories import TagFactory
from unit_collections.documents import Collection
from unit_collections.factories import CollectionFactory
from units.documents import Unit
from units.factories import UnitFactory


class UnitTest(BaseTestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        self.tag = TagFactory(lab=self.lab)

    def test_create(self):
        url = reverse('units:create', kwargs={'lab_pk': self.lab.pk})
        data = {
            'data-0-Sample': random.randint(1, 100),
            'data-0-Experiments': self.experiment.__unicode__(),
            'data-0-Tags': self.tag.__unicode__(),
            'data-0-experiments_pk[]': unicode(self.experiment.pk),
            'data-0-tags_pk[]': unicode(self.tag.pk),
            'data-1-Sample': random.randint(1, 100),
            'data-1-Experiments': self.experiment.__unicode__(),
            'data-1-Tags': self.tag.__unicode__(),
            'data-1-experiments_pk[]': unicode(self.experiment.pk),
            'data-1-tags_pk[]': unicode(self.tag.pk),
            'length': 2
        }

        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Unit.objects.count(), 2)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Unit.objects.count(), 4)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, json.dumps([[0, {"errors": {"non_field_error": "Permission denied"}, "success": False}],
                                [1, {"errors": {"non_field_error": "Permission denied"}, "success": False}]]))
        self.assertEqual(Unit.objects.count(), 4)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Unit.objects.count(), 4)

        self.experiment.viewers.append(self.guest)
        self.experiment.save()
        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, json.dumps([[0, {"errors": {"non_field_error": "Permission denied"}, "success": False}],
                                [1, {"errors": {"non_field_error": "Permission denied"}, "success": False}]]))
        self.assertEqual(Unit.objects.count(), 4)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Unit.objects.count(), 4)

        self.experiment.editors.append(self.guest)
        self.experiment.save()
        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Unit.objects.count(), 6)

    def test_create_not_valid(self):
        url = reverse('units:create', kwargs={'lab_pk': self.lab.pk})
        self.client.login(username=self.owner.email, password='qwerty')
        data = {
            'data-0-Tags': self.tag.__unicode__(),
            'data-0-experiments_pk[]': unicode(self.experiment.pk),
            'data-0-tags_pk[]': unicode(self.tag.pk),
            'length': 1
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Unit.objects.count(), 0)
        self.assertEqual(resp.content, json.dumps([[0, {"errors": {"sample": ["This field is required."]}, "success": False}]]))

    def test_update(self):
        unit = UnitFactory(experiments=[self.experiment], lab=self.lab, user=self.owner)
        url = reverse('units:create', kwargs={'lab_pk': self.lab.pk})
        data = {
            'data-0-pk': unicode(unit.pk),
            'data-0-comment': random.randint(1, 100),
            'data-0-Sample': random.randint(1, 100),
            'data-0-Experiments': self.experiment.__unicode__(),
            'data-0-Tags': self.tag.__unicode__(),
            'data-0-experiments_pk[]': unicode(self.experiment.pk),
            'data-0-tags_pk[]': unicode(self.tag.pk),
            'length': 1
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Unit.objects.count(), 1)
        new_unit = Unit.objects.get(pk=unit.pk)
        self.assertEqual(new_unit.sample, unicode(data['data-0-Sample']))

        self.client.login(username=self.member.email, password='qwerty')
        data['data-0-Sample'] = random.randint(1, 100)
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Unit.objects.count(), 1)
        unit = Unit.objects.get(pk=unit.pk)
        self.assertEqual(unit.sample, unicode(data['data-0-Sample']))

        self.client.login(username=self.guest.email, password='qwerty')
        data['data-0-Sample'] = random.randint(1, 10)
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, json.dumps([[0, {"errors": {"non_field_error": "Permission denied"}, "success": False}],
                                                  [0, {"errors": {"non_field_error": "Permission denied"}, "success": False}]]))
        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)

    # def test_update_description(self):
    #     unit = UnitFactory(experiments=[self.experiment], lab=self.lab, user=self.owner)
    #     url = reverse('units:detail', kwargs={'pk': unit.pk, 'lab_pk': self.lab.pk})
    #     data = {
    #         'description': lorem_ipsum.words(1, False)
    #     }
    #     resp = self.client.post(url, data, follow=True)
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertContains(resp, _('Login'))
    #
    #     self.client.login(username=self.owner.email, password='qwerty')
    #     resp = self.client.post(url, data, follow=True)
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertEqual(Unit.objects.count(), 1)
    #     new_unit = Unit.objects.get(pk=unit.pk)
    #     self.assertEqual(new_unit.description, unicode(data['description']))
    #
    #     self.client.login(username=self.member.email, password='qwerty')
    #     data['description'] = lorem_ipsum.words(1, False)
    #     resp = self.client.post(url, data, follow=True)
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertEqual(Unit.objects.count(), 1)
    #     new_unit = Unit.objects.get(pk=unit.pk)
    #     self.assertEqual(new_unit.description, unicode(data['description']))
    #
    #     self.client.login(username=self.guest.email, password='qwerty')
    #     data['description'] = lorem_ipsum.words(1, False)
    #     resp = self.client.post(url, data, follow=True)
    #     self.assertEqual(resp.status_code, 403)
    #
    #     self.client.login(username=self.user4.email, password='qwerty')
    #     resp = self.client.post(url, data, follow=True)
    #     self.assertEqual(resp.status_code, 403)

    def test_delete(self):
        unit = UnitFactory(experiments=[self.experiment], lab=self.lab, user=self.owner)
        collection = CollectionFactory(lab=self.lab, user=self.owner, owners=[self.owner], units=[unit])
        url = reverse('units:delete', kwargs={'lab_pk': self.lab.pk})

        resp = self.client.post(url, {'data': [unicode(unit.pk)]}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, {'data': [unicode(unit.pk)]}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, json.dumps({"data": [{"errors": {"non_field_error": "Permission denied"}, "success": False}], "success": True}))

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, {'data': [unicode(unit.pk)]}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, json.dumps({"data": [{"errors": {"non_field_error": "Permission denied"}, "success": False}], "success": True}))

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, {'data': [unicode(unit.pk)]}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, json.dumps({"data": [{"errors": {"non_field_error": "Permission denied"}, "success": False}], "success": True}))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, {'data': [unicode(unit.pk)]}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Unit.objects.count(), 1)
        self.assertEqual(Collection.objects.get(pk=collection.pk).units, [])
        self.assertFalse(Unit.objects.get(pk=unit.pk).active)

    def test_delete_one(self):
        unit = UnitFactory(experiments=[self.experiment], lab=self.lab, user=self.owner)
        url = reverse('units:delete-one', kwargs={'lab_pk': self.lab.pk, 'pk': unit.pk})

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
        self.assertEqual(Unit.objects.count(), 1)
        self.assertFalse(Unit.objects.get(pk=unit.pk).active)

    def test_detail(self):
        unit = UnitFactory(experiments=[self.experiment], lab=self.lab, user=self.owner)
        url = reverse('units:detail', kwargs={'pk': unit.pk, 'lab_pk': self.lab.pk})

        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_list(self):
        unit = UnitFactory.create_batch(2, experiments=[self.experiment], lab=self.lab, user=self.owner)
        url = reverse('units:list', kwargs={'lab_pk': self.lab.pk})

        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, unicode(unit[0].pk), 2)
        self.assertContains(resp, unicode(unit[1].pk), 2)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, unicode(unit[0].pk), 2)
        self.assertContains(resp, unicode(unit[1].pk), 2)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "data-content='[]'", 1)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)

