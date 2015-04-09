import json

from django.contrib.webdesign import lorem_ipsum
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, ugettext

from unit_collections.documents import Collection
from unit_collections.factories import CollectionFactory
from common.testcase import BaseTestCase
from experiments.factories import ExperimentFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory
from units.factories import UnitFactory


class CollectionTest(BaseTestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        self.units = UnitFactory.create_batch(10, lab=self.lab, user=self.owner, experiments=[self.experiment])

    def test_create(self):
        url = reverse('collections:create', kwargs={'lab_pk': self.lab.pk})
        data = {
            'title': lorem_ipsum.words(3, False),
            'units': [unicode(unit.pk) for unit in self.units],
            'owners': [self.owner.pk],
        }

        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _(u'You have not permission to add this units {} in your '
                                    u'collection'.format(','.join([unit.__unicode__() for unit in self.units]))), 1)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertContains(resp, _(u'Select a valid choice. {} is not one of the available choices.'.format(self.units[0].pk)), 1)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Collection.objects.count(), 1)

    def test_create_with_perm(self):
        experiment1 = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.member.pk], viewers=[self.guest.pk])
        unit1 = UnitFactory(lab=self.lab, user=self.owner, experiments=[experiment1])

        experiment2 = ExperimentFactory(lab=self.lab, owners=[self.member.pk])
        unit2 = UnitFactory(lab=self.lab, user=self.member, experiments=[experiment2])

        url = reverse('collections:create', kwargs={'lab_pk': self.lab.pk})
        data = {
            'title': lorem_ipsum.words(3, False),
            'units': [unicode(unit1.pk), unicode(unit2.pk)],
            'owners': [self.owner.pk],
        }

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.count(), 2)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _(u'Select a valid choice. {} is not one of the available choices.'.format(unit2.pk)), 1)
        self.assertEqual(Collection.objects.count(), 2)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Collection.objects.count(), 2)

    def test_update(self):
        experiment1 = ExperimentFactory(lab=self.lab, owners=[self.member.pk])
        unit1 = UnitFactory(lab=self.lab, user=self.owner, experiments=[experiment1])
        collection = CollectionFactory(lab=self.lab, user=self.member, owners=[self.member], units=[unit1])
        url = reverse('collections:update', kwargs={'lab_pk': self.lab.pk, 'pk': collection.pk})

        data = {
            'title': lorem_ipsum.words(3, False),
            'units': [unicode(unit.pk) for unit in collection.units],
            'owners': [self.owner.pk],
        }

        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.first().title, data['title'])
        self.assertEqual(Collection.objects.count(), 1)

        data['title'] = lorem_ipsum.words(3, False)
        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.first().title, data['title'])
        self.assertEqual(Collection.objects.count(), 1)

        data['title'] = lorem_ipsum.words(3, False)
        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _(u'Select a valid choice. {} is not one of the available choices.'.format(unit1.pk)), 1)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Collection.objects.count(), 1)

    def test_update_with_perm(self):
        experiment1 = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.member.pk], viewers=[self.guest.pk])
        unit1 = UnitFactory(lab=self.lab, user=self.owner, experiments=[experiment1])

        experiment2 = ExperimentFactory(lab=self.lab, owners=[self.member.pk])
        unit2 = UnitFactory(lab=self.lab, user=self.member, experiments=[experiment2])

        collection = CollectionFactory(lab=self.lab, user=self.member, units=[unicode(unit1.pk), unicode(unit2.pk)], owners=[self.owner])
        url = reverse('collections:update', kwargs={'lab_pk': self.lab.pk, 'pk': collection.pk})

        data = {
            'title': lorem_ipsum.words(3, False),
            'units': [unicode(unit.pk) for unit in collection.units],
            'owners': [self.member.pk],
        }

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _(u'Select a valid choice. {} is not one of the available choices.'.format(unit2.pk)), 1)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Collection.objects.count(), 1)

    def test_delete(self):
        collection = CollectionFactory(lab=self.lab, user=self.owner, owners=[self.owner])
        url = reverse('collections:delete', kwargs={'lab_pk': self.lab.pk})
        data = {'ids[]': [unicode(collection.pk)]}
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        data = {'ids[]': [unicode(collection.pk)]}
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.count(), 0)

        self.client.login(username=self.member.email, password='qwerty')
        collection = CollectionFactory(lab=self.lab, user=self.owner, owners=[self.owner])
        data = {'ids[]': [unicode(collection.pk)]}
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Collection.objects.count(), 1)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Collection.objects.count(), 1)

    def test_list(self):
        experiment1 = ExperimentFactory(lab=self.lab, owners=[self.owner.pk])
        unit1 = UnitFactory(lab=self.lab, user=self.owner, experiments=[experiment1])
        collection1 = CollectionFactory(lab=self.lab, user=self.owner, owners=[self.owner], units=[unit1])

        experiment2 = ExperimentFactory(lab=self.lab, owners=[self.member.pk])
        unit2 = UnitFactory(lab=self.lab, user=self.member, experiments=[experiment2])
        collection2 = CollectionFactory(lab=self.lab, user=self.owner, owners=[self.owner], units=[unit2])

        result = []
        for data in [collection1, collection2]:
            result.append({
                "text": data.title,
                "a_attr": {
                    "href": data.get_absolute_url()
                },
                "id": unicode(data.pk),
                "parent": "#",
                "icon": False
            })
        result = json.dumps(result)
        url = reverse('collections:list', kwargs={'lab_pk': self.lab.pk})
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, _('Login'))

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, result, 1)
        self.assertEqual(Collection.objects.count(), 2)

        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, {
                "text": collection2.title,
                "a_attr": {
                    "href": collection2.get_absolute_url()
                },
                "id": unicode(collection2.pk),
                "parent": "#",
                "icon": False
            }, 1)
        self.assertEqual(Collection.objects.count(), 2)

        self.client.login(username=self.guest.email, password='qwerty')
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, result, 0)
        self.assertEqual(Collection.objects.count(), 2)

        self.client.login(username=self.user4.email, password='qwerty')
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Collection.objects.count(), 2)

    def test_change_owners_by_editor(self):
        """
        Check Editors can't change owners in experiments
        """
        collection = CollectionFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.member.pk], user=self.owner, units=self.units)
        url = reverse('collections:update', kwargs={'lab_pk': self.lab.pk, 'pk': collection.pk})
        data = {
            'owners': [self.member.pk],
            'editors': [self.owner.pk],
            'description': lorem_ipsum.words(2),
            'title': lorem_ipsum.words(2),
        }
        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'You have not permission change owners', 1)
        self.assertEqual(Collection.objects.first().owners, [self.owner])
