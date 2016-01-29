from time import sleep
from elasticutils.contrib.django.estestcase import ESTestCase
from django.conf import settings
from django.test import TestCase
from django.utils import lorem_ipsum
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.test.utils import override_settings
from django.core.management import call_command
from experiments.models import Experiment
from experiments.factories import ExperimentFactory
from comments.factories import CommentFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory
from units.factories import UnitFactory


class TestQueries(ESTestCase):

    def setUp(self):
        settings.ES_DISABLED = False
        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
        settings.CELERY_ALWAYS_EAGER = True
        settings.BROKER_BACKEND = 'memory'

        call_command('createesindex')
        self.owner = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk])
        self.experiment = ExperimentFactory(**{
            'owners': [self.owner.pk],
            'description': lorem_ipsum.words(2),
            'title': 'qwerty #1',
        })

        sleep(1)
        self.client.login(username=self.owner.email, password='qwerty')

    def test_experiment(self):
        self.client.login(username=self.owner.email, password='qwerty')
        self.assertEqual(Experiment.objects.count(), 1)
        url = u'{}?q=qwerty'.format(reverse('search:all', kwargs={'lab_pk': self.lab.pk}))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, u'qwerty', 3)

    def test_unit(self):

        unit = UnitFactory(experiments=[self.experiment], lab=self.lab, sample=u'ytrewq')
        sleep(1)
        url = u'{}?q=ytrewq'.format(reverse('search:all', kwargs={'lab_pk': self.lab.pk}))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, u'ytrewq', 4)

    def test_comment(self):
        comment = CommentFactory(object_id=self.experiment.id, init_user=self.owner, text='textofcomment')
        sleep(1)
        url = u'{}?q=textofcomment'.format(reverse('search:all', kwargs={'lab_pk': self.lab.pk}))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, u'textofcomment', 2)

#todo: profiles