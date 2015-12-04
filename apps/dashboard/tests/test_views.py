from django.utils import lorem_ipsum
from django.core.urlresolvers import reverse

from labs.factories import LabFactory
from common.testcase import BaseTestCase
from profiles.factories import UserFactory
from profiles.factories import UserFactory
from experiments.factories import ExperimentFactory


class TestDashboardTest(BaseTestCase):
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
        self.assertContains(resp, u'resent-activities-container')  # TODO: fix typo
        self.assertContains(resp, u'Storages')
        self.client.login(username=self.member.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, self.lab.name)
        self.assertContains(resp, u'<div id="calendar"')
        self.assertContains(resp, u'resent-activities-container')  # TODO: fix typo
        self.assertContains(resp, u'Storages')

    def test_recent_experiment_activity_view(self):

        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])

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
        self.assertContains(resp, self.owner.full_name.title())
        self.assertContains(resp, experiment.title)

    def test_recent_comment_activity_view(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])

        url = reverse('dashboard:comment-activity', kwargs={'lab_pk': self.lab.pk})
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200)
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.get(url)
        self.assertContains(resp, u'timeline')

        # Add comment
        comment_url = reverse('comment:comment', kwargs={'lab_pk': self.lab.pk})
        text = lorem_ipsum.words(2)
        data = {
            'create-text': text,
            'create-instance_type': 'Experiment',
            'create-object_id': unicode(experiment.pk)
        }

        resp = self.client.post(comment_url, data, follow=True)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(url)
        self.assertContains(resp, self.owner.full_name.title())
        self.assertContains(resp, text)

    def test_recent_comment_activity_experiment_view(self):
        experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], editors=[self.guest.pk])

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
        comment_url = reverse('comment:comment', kwargs={'lab_pk': self.lab.pk})
        text = lorem_ipsum.words(2)
        data = {
            'create-text': text,
            'create-instance_type': 'Experiment',
            'create-object_id': unicode(experiment.pk)
        }

        resp = self.client.post(comment_url, data, follow=True)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(url)
        self.assertContains(resp, self.owner.full_name.title())
        self.assertContains(resp, text)

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
        self.assertContains(resp, self.owner.full_name.title())
        self.assertContains(resp, experiment.title)

        # Add comment
        comment_url = reverse('comment:comment', kwargs={'lab_pk': self.lab.pk})
        text = lorem_ipsum.words(2)
        data = {
            'create-text': text,
            'create-instance_type': 'Experiment',
            'create-object_id': unicode(experiment.pk)
        }

        resp = self.client.post(comment_url, data, follow=True)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(url)
        self.assertContains(resp, self.owner.full_name.title())
        self.assertContains(resp, text)
