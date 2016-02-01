from django.test import TestCase
from django.utils import lorem_ipsum
from django.core.urlresolvers import reverse
from django.template.defaultfilters import title
from labs.factories import LabFactory
from profiles.factories import UserFactory
from profiles.factories import UserFactory
from experiments.factories import ExperimentFactory


class TestDashboardTest(TestCase):
    def setUp(self):
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()

        data = {
            'name': lorem_ipsum.words(1, False),
            'investigator': [self.owner.pk],
            'members': [self.member.pk],
        }
        self.lab = LabFactory(**data)

    def test_dashboard(self):
        url = reverse('dashboard:dashboard', kwargs={'lab_pk': self.lab.pk})

        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, self.lab.name)
        self.assertContains(resp, u'<div id="calendar"')
        self.assertContains(resp, u'recent-activities-container')
        self.assertContains(resp, u'Storages')
        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, self.lab.name)
        self.assertContains(resp, u'<div id="calendar"')
        self.assertContains(resp, u'recent-activities-container')
        self.assertContains(resp, u'Storages')

    def test_recent_experiment_activity_view(self):

        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])
        experiment2 = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])

        url = reverse('dashboard:experiment-all-activity', kwargs={'lab_pk': self.lab.pk, 'experiment_pk': experiment.pk})
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, u'timeline')

        #Update experiment
        exp_url = reverse('experiments:update', kwargs={'lab_pk': self.lab.pk, 'pk': experiment.pk})
        data = {
            'owners': [self.owner.pk],
            'start': experiment.start.strftime('%m/%d/%Y %H:%M'),
            'end': experiment.end.strftime('%m/%d/%Y %H:%M'),
            'description': lorem_ipsum.words(2),
            'title': experiment.title,
            'status': experiment.status
        }
        resp = self.client.post(exp_url, data, follow=True)
        resp = self.client.get(url)
        self.assertContains(resp, title(self.owner.full_name))
        self.assertContains(resp, experiment.title)

        #Update experiment2
        exp_url = reverse('experiments:update', kwargs={'lab_pk': self.lab.pk, 'pk': experiment2.pk})
        data = {
            'owners': [self.owner.pk],
            'start': experiment.start.strftime('%m/%d/%Y %H:%M'),
            'end': experiment.end.strftime('%m/%d/%Y %H:%M'),
            'description': lorem_ipsum.words(2),
            'title': experiment2.title,
            'status': experiment.status
        }
        resp = self.client.post(exp_url, data, follow=True)
        resp = self.client.get(url)
        self.assertNotContains(resp, experiment2.title)

    def test_recent_comment_activity_view(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])

        url = reverse('dashboard:comment-activity', kwargs={'lab_pk': self.lab.pk})
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, u'timeline')

        # Add comment
        text = lorem_ipsum.words(2)
        comment_url = reverse('comment:api-list', kwargs={
            'lab_pk': self.lab.pk,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        })
        data = {
            'text': text,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        }
        resp = self.client.post(comment_url, data, format='json')
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get(url)
        self.assertContains(resp, title(self.owner.full_name))
        self.assertContains(resp, text)

    def test_recent_comment_activity_experiment_view(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])
        experiment2 = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])

        url = reverse('dashboard:experiment-comment-activity',
                      kwargs={'lab_pk': self.lab.pk,
                              'experiment_pk': experiment.pk
                              }
                      )
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, u'timeline')

        # Add comment
        text = lorem_ipsum.words(2)
        comment_url = reverse('comment:api-list', kwargs={
            'lab_pk': self.lab.pk,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        })
        data = {
            'text': text,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        }
        resp = self.client.post(comment_url, data, format='json')
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get(url)
        self.assertContains(resp, title(self.owner.full_name))
        self.assertContains(resp, text)

        # Add comment to exp2
        text = 'some text'
        comment_url = reverse('comment:api-list', kwargs={
            'lab_pk': self.lab.pk,
            'instance_type': 'experiment',
            'object_id': experiment2.pk,
        })
        data = {
            'text': text,
            'instance_type': 'experiment',
            'object_id': experiment2.pk,
        }
        resp = self.client.post(comment_url, data, format='json')
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get(url)
        self.assertNotContains(resp, text)

    def test_recent_all_activity_view(self):

        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])

        url = reverse('dashboard:all-activity', kwargs={'lab_pk': self.lab.pk})
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, u'timeline')

        #Update experiment
        exp_url = reverse('experiments:update', kwargs={'lab_pk': self.lab.pk, 'pk': experiment.pk})
        data = {
            'owners': [self.owner.pk],
            'start': experiment.start.strftime('%m/%d/%Y %H:%M'),
            'end': experiment.end.strftime('%m/%d/%Y %H:%M'),
            'description': lorem_ipsum.words(2),
            'title': experiment.title,
            'status': experiment.status
        }
        resp = self.client.post(exp_url, data, follow=True)
        resp = self.client.get(url)
        self.assertContains(resp, title(self.owner.full_name))
        self.assertContains(resp, experiment.title)

        # Add comment
        text = lorem_ipsum.words(2)
        comment_url = reverse('comment:api-list', kwargs={
            'lab_pk': self.lab.pk,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        })
        data = {
            'text': text,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        }
        resp = self.client.post(comment_url, data, format='json')
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get(url)
        self.assertContains(resp, title(self.owner.full_name))
        self.assertContains(resp, text)

    def test_recent_unit_activity(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])
        experiment2 = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])

        url = reverse('dashboard:experiment-comment-activity',
                      kwargs={'lab_pk': self.lab.pk,
                              'experiment_pk': experiment.pk
                              }
                      )
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, u'timeline')

        # Add comment
        text = lorem_ipsum.words(2)
        comment_url = reverse('comment:api-list', kwargs={
            'lab_pk': self.lab.pk,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        })
        data = {
            'text': text,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        }
        resp = self.client.post(comment_url, data, format='json')
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get(url)
        self.assertContains(resp, title(self.owner.full_name))
        self.assertContains(resp, text)

        # Add comment to exp2
        text = 'some text'
        comment_url = reverse('comment:api-list', kwargs={
            'lab_pk': self.lab.pk,
            'instance_type': 'experiment',
            'object_id': experiment.pk,
        })
        data = {
            'text': text,
            'instance_type': 'experiment',
            'object_id': experiment2.pk,
        }
        resp = self.client.post(comment_url, data, format='json')
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get(url)
        self.assertNotContains(resp, text)

# TODO: measurement, units, pagination