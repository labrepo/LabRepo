from django.conf import settings
from django.test import TestCase
# from django_selenium.testcases import SeleniumTestCase

from pymongo import Connection


class TestMixin(object):

    def _fixture_teardown(self):
        pass

    def _post_teardown(self):
        self._fixture_teardown()

    def _fixture_setup(self):
        pass

    def tearDown(self):
        conn = Connection()
        conn.drop_database(settings._MONGODB_NAME)
        conn.disconnect()


class BaseTestCase(TestMixin, TestCase):
    pass


# class SeleniumBaseTestCase(TestMixin, SeleniumTestCase):
#     def tearDown(self):
#         super(SeleniumBaseTestCase, self).tearDown()
#         self.driver.quit()
#
#     def _fixture_setup(self):
#         return super(SeleniumTestCase, self)._fixture_setup()
