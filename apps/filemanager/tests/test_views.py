import os
import json

from django.contrib.webdesign import lorem_ipsum
from django.core.urlresolvers import reverse
from django.conf import settings

from labs.documents import Lab
from common.testcase import BaseTestCase
from profiles.factories import UserFactory
from profiles.factories import UserFactory


class TestFilemanagerBackendTest(BaseTestCase):
    def setUp(self):
        self.owner = UserFactory()

        url = reverse('labs:create')
        data = {
            'name': lorem_ipsum.words(1, False),
            'investigator': [self.owner.pk],
            # 'members': [self.member.pk],
        }
        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, data, follow=True)
        self.lab = Lab.objects.get(name=data['name'])

        with open(os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, unicode(self.lab.pk) + '/', 'testfile1.txt'), 'w') as f:
            f.write('test file content')
        os.makedirs(os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, unicode(self.lab.pk) + '/', 'test dir'))
        with open(os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, unicode(self.lab.pk) + '/', 'test dir', 'testfile2.txt'), 'w') as f:
            f.write('test file content in dir')

        self.client.logout()

    def tearDown(self):
        super(TestFilemanagerBackendTest, self).tearDown()
        print('td')

    def get_directory_content(self, directory='/'):
        if directory == '/' or not directory:
            return os.listdir(os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, unicode(self.lab.pk) + '/'))
        else:
            return os.listdir(os.path.join(settings.FILEMANAGER_UPLOAD_ROOT, unicode(self.lab.pk) + '/', directory))

    def test_list_file(self):

        url = reverse('filemanager-list', kwargs={'lab_pk': self.lab.pk})
        #
        data = {
            'params': {'mode': 'list', 'onlyFolders': False, 'path': '/'}
        }

        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")
        self.assertNotEqual(resp.status_code, 200)

        self.client.login(username=self.owner.email, password='qwerty')
        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'testfile1.txt')
        self.assertContains(resp, 'test dir')
        self.assertNotContains(resp, 'testfile2.txt')

        data = {
            'params': {'mode': 'list', 'onlyFolders': False, 'path': '/test dir'}
        }

        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'testfile2')
        self.assertNotContains(resp, 'testfile1')

        #todo: check urls

    def test_create_folder(self):

        url = reverse('filemanager-createfolder', kwargs={'lab_pk': self.lab.pk})

        # in root dir
        data = {
            'params': {'mode': 'addfolder', 'name': 'created_folder', 'path': ''}
        }
        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")

        self.assertNotEqual(resp.status_code, 200)
        self.assertNotIn('created_folder', self.get_directory_content('/'))

        self.client.login(username=self.owner.email, password='qwerty')

        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")

        self.assertEqual(resp.status_code, 200)
        self.assertIn('created_folder', self.get_directory_content('/'))

        # in dir
        data = {
            'params': {'mode': 'addfolder', 'name': 'created_folder2', 'path': '/test dir'}
        }
        self.client.logout()
        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")
        self.assertNotEqual(resp.status_code, 200)
        self.assertNotIn('created_folder2', self.get_directory_content('test dir'))

        self.client.login(username=self.owner.email, password='qwerty')

        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")

        self.assertEqual(resp.status_code, 200)
        self.assertIn('created_folder2', self.get_directory_content('test dir'))

    def test_rename(self):

        url = reverse('filemanager-rename', kwargs={'lab_pk': self.lab.pk})

        # rename file
        data = {
            'params': {'mode': 'rename', 'path': '/testfile1.txt', 'newPath': '/renamed_file.txt'}
        }
        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")
        self.assertNotEqual(resp.status_code, 200)
        self.assertNotIn('renamed_file.txt', self.get_directory_content('/'))

        self.client.login(username=self.owner.email, password='qwerty')

        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")

        self.assertEqual(resp.status_code, 200)
        self.assertIn('renamed_file.txt', self.get_directory_content('/'))
        self.assertNotIn('testfile1.txt', self.get_directory_content('/'))

        # rename dir
        data = {
            'params': {'mode': 'rename', 'path': '/test dir', 'newPath': '/renamed dir'}
        }
        self.client.logout()
        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")
        self.assertNotEqual(resp.status_code, 200)
        self.assertNotIn('renamed dir', self.get_directory_content('/'))

        self.client.login(username=self.owner.email, password='qwerty')

        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")

        self.assertEqual(resp.status_code, 200)
        self.assertIn('renamed dir', self.get_directory_content('/'))
        self.assertNotIn('test dir', self.get_directory_content('/'))

    def test_remove(self):

        url = reverse('filemanager-remove', kwargs={'lab_pk': self.lab.pk})

        # remove file
        data = {
            'params': {'mode': 'delete', 'path': '/test dir/testfile2.txt'}
        }
        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")
        self.assertNotEqual(resp.status_code, 200)
        self.assertIn('testfile2.txt', self.get_directory_content('test dir'))

        self.client.login(username=self.owner.email, password='qwerty')

        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")

        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('testfile2.txt', self.get_directory_content('test dir'))

        # remove dir
        data = {
            'params': {'mode': 'delete', 'path': '/test dir'}
        }

        self.client.logout()
        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")
        self.assertNotEqual(resp.status_code, 200)
        self.assertIn('test dir', self.get_directory_content('/'))

        self.client.login(username=self.owner.email, password='qwerty')

        resp = self.client.post(url, json.dumps(data),
                                content_type="application/json")

        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('test dir', self.get_directory_content('/'))

        # TODO: remove not empty dir