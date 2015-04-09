from django.contrib.webdesign import lorem_ipsum
from django.core.urlresolvers import reverse
from django_selenium.testcases import wait

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from common.testcase import SeleniumBaseTestCase
from experiments.factories import ExperimentFactory
from labs.factories import LabFactory
from profiles.factories import UserFactory
from units.documents import Unit


class UnitSeleniumTest(SeleniumBaseTestCase):
    def setUp(self):
        super(UnitSeleniumTest, self).setUp()
        self.owner = UserFactory()
        self.member = UserFactory()
        self.guest = UserFactory()
        self.user4 = UserFactory()
        self.lab = LabFactory(investigator=[self.owner.pk], members=[self.member.pk], guests=[self.guest.pk])
        self.experiment = ExperimentFactory(lab=self.lab, owners=[self.owner.pk], viewers=[self.guest.pk])

        self.driver.authorize(username=self.owner.email, password='qwerty')
        self.driver.open_url(reverse('units:list', kwargs={'lab_pk': unicode(self.lab.pk)}))

    def create(self, tr):
        self.tds = tr.find_elements_by_tag_name('td')

        actions = ActionChains(self.driver)
        actions.move_to_element(self.tds[1])
        actions.double_click()
        actions.send_keys(lorem_ipsum.words(1, False))
        actions.perform()

        actions.move_to_element(self.tds[2])
        actions.double_click()
        actions.perform()

        self.driver.select('select.htSelectEditor', unicode(self.experiment.pk))
        self.driver.click('body')

    @wait
    def create_units(self, table):
        # create units
        for i in range(5):
            tr = table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(i + 1) + ')')
            self.create(tr)
        self.driver.find_element_by_css_selector('#save').click()
        units = Unit.objects.filter(lab=self.lab.pk)
        for i, unit in enumerate(units):
            td = self.driver.find('.htCore tbody tr:nth-child(' + str(i + 1) + ') td:nth-child(1)')
            self.assertEqual(td.text, unicode(unit.pk))
        self.assertEqual(units.count(), 5)
        return units

    # def test_create_success(self):
    #     table = self.driver.find_element_by_id('dataTable')
    #     tr = table.find_element_by_css_selector('.htCore tbody tr')
    #     self.create(tr)
    #     self.driver.click('#save')
    #     unit = Unit.objects.get(lab=self.lab.pk)
    #     self.wait_for_text('.htCore tbody tr:nth-child(2) td:nth-child(1)', unicode(unit.pk))
    #     # self.assertEqual(self.driver.find('div.alert-success').text, 'Success')
    #     self.assertEqual(self.tds[0].text, unicode(unit.pk))
    #
    # def test_update_success(self):
    #     table = self.driver.find_element_by_id('dataTable')
    #     units = self.create_units(table)
    #     # update units
    #     for i in range(5):
    #         tr = table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(i + 1) + ')')
    #         actions = ActionChains(self.driver)
    #         actions.move_to_element(tr.find_element_by_css_selector('td:nth-child(2)'))
    #         actions.double_click()
    #         actions.send_keys(lorem_ipsum.words(1, False))
    #         actions.move_to_element(tr.find_element_by_css_selector('td:nth-child(7)'))
    #         actions.double_click()
    #         actions.send_keys(lorem_ipsum.words(1, False))
    #         actions.perform()
    #     self.driver.click('#save')
    #     updated_units = Unit.objects.filter(lab=self.lab.pk)
    #     for i, unit in enumerate(updated_units):
    #         td = self.driver.find('.htCore tbody tr:nth-child(' + str(i + 1) + ') td:nth-child(1)')
    #         self.assertEqual(td.text, unicode(unit.pk))
    #         self.assertEqual(units[i].pk, unit.pk)
    #     self.assertEqual(units.count(), 5)
    #
    # def test_create_error(self):
    #     table = self.driver.find_element_by_id('dataTable')
    #     for i in range(5):
    #         tr = table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(i + 1) + ')')
    #         self.tds = tr.find_elements_by_tag_name('td')
    #         actions = ActionChains(self.driver)
    #         actions.move_to_element(self.tds[2])
    #         actions.double_click()
    #         actions.perform()
    #         self.driver.select('select.htSelectEditor', unicode(self.experiment.pk))
    #         self.driver.click('body')
    #     self.driver.click('#save')
    #     self.assertEqual(Unit.objects.count(), 0)
    #     for i in range(5):
    #         td = self.driver.find('.htCore tbody tr:nth-child(' + str(i + 1) + ') td:nth-child(2)')
    #         self.assertEqual(td.get_attribute('title'), 'This field is required.')
    #         self.assertIn('error', td.get_attribute('class'))
    #
    # def test_create_error_with_blank_tr(self):
    #     table = self.driver.find_element_by_id('dataTable')
    #     for i in range(0, 6, 2):
    #         tds = table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(i + 1) + ')').find_elements_by_tag_name('td')
    #         actions = ActionChains(self.driver)
    #         actions.move_to_element(tds[2])
    #         actions.double_click()
    #         actions.perform()
    #         self.driver.select('select.htSelectEditor', unicode(self.experiment.pk))
    #         self.driver.click('body')
    #
    #         tds = table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(i + 2) + ')').find_elements_by_tag_name('td')
    #         actions = ActionChains(self.driver)
    #         actions.move_to_element(tds[1])
    #         actions.double_click()
    #         actions.send_keys(Keys.RETURN)
    #         actions.perform()
    #
    #     self.driver.click('#save')
    #     self.assertEqual(Unit.objects.count(), 0)
    #     for i in range(6):
    #         td = self.driver.find('.htCore tbody tr:nth-child(' + str(i + 1) + ') td:nth-child(2)')
    #         if not i % 2:
    #             self.assertEqual(td.get_attribute('title'), 'This field is required.')
    #             self.assertIn('error', td.get_attribute('class'))
    #         else:
    #             self.assertEqual(td.get_attribute('title'), '')
    #             self.assertNotIn('error', td.get_attribute('class'))
    #
    # def test_update_error(self):
    #     table = self.driver.find_element_by_id('dataTable')
    #     self.create_units(table)
    #
    #     for i in range(5):
    #         tr = table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(i + 1) + ')')
    #         actions = ActionChains(self.driver)
    #         actions.move_to_element(tr.find_element_by_css_selector('td:nth-child(2)'))
    #         actions.double_click()
    #         actions.send_keys(lorem_ipsum.words(1, False))
    #         actions.perform()
    #     self.driver.click('#save')
    #
    #     for i in range(5):
    #         td = self.driver.find('.htCore tbody tr:nth-child(' + str(i + 1) + ') td:nth-child(7)')
    #         self.assertEqual(td.get_attribute('title'), 'This field is required.')
    #         self.assertIn('error', td.get_attribute('class'))
    #
    # def test_create_permission(self):
    #     self.driver.authorize(username=self.guest.email, password='qwerty')
    #     self.driver.open_url(reverse('units:list', kwargs={'lab_pk': unicode(self.lab.pk)}))
    #     self.assertFalse(self.driver.is_element_present('#save'))
    #
    # def test_update_permission(self):
    #     table = self.driver.find_element_by_id('dataTable')
    #     self.create_units(table)
    #     self.driver.authorize(username=self.guest.email, password='qwerty')
    #     self.driver.open_url(reverse('units:list', kwargs={'lab_pk': unicode(self.lab.pk)}))
    #     table = self.driver.find_element_by_id('dataTable')
    #     tr = table.find_element_by_css_selector('.htCore tbody tr:nth-child(1)')
    #     text = tr.find_element_by_css_selector('td:nth-child(2)').text
    #     actions = ActionChains(self.driver)
    #     actions.move_to_element(tr.find_element_by_css_selector('td:nth-child(2)'))
    #     actions.double_click()
    #     actions.send_keys(lorem_ipsum.words(1, False))
    #     actions.perform()
    #     self.assertEqual(tr.find_element_by_css_selector('td:nth-child(2)').text, text)
    #     self.assertFalse(self.driver.is_element_present('#save'))

    # def test_create_and_update_parent(self):
    #     pass

    def test_remove_success(self):
        table = self.driver.find_element_by_id('dataTable')
        self.create_units(table)

        tr = table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(3) + ')')
        actions = ActionChains(self.driver)
        actions.move_to_element(tr.find_element_by_css_selector('td:nth-child(2)'))
        actions.click()
        actions.key_down(Keys.SHIFT)
        actions.move_to_element(table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(5) + ') td:nth-child(3)'))
        actions.click()
        actions.key_up(Keys.SHIFT)
        actions.move_to_element(table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(4) + ') td:nth-child(3)'))
        actions.context_click().send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        self.assertEqual(len(self.driver.find_elements_by_css_selector('.htCore tbody tr')), 3 * 2)

    def test_remove_permission(self):
        table = self.driver.find_element_by_id('dataTable')
        self.create_units(table)
        self.driver.authorize(username=self.guest.email, password='qwerty')
        self.driver.open_url(reverse('units:list', kwargs={'lab_pk': unicode(self.lab.pk)}))
        table = self.driver.find_element_by_id('dataTable')
        tr = table.find_element_by_css_selector('.htCore tbody tr:nth-child(1)')
        actions = ActionChains(self.driver)
        actions.move_to_element(tr.find_element_by_css_selector('td:nth-child(2)'))
        actions.click()
        actions.key_down(Keys.SHIFT)
        actions.move_to_element(table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(5) + ') td:nth-child(3)'))
        actions.click()
        actions.key_up(Keys.SHIFT)
        actions.move_to_element(table.find_element_by_css_selector('.htCore tbody tr:nth-child(' + str(4) + ') td:nth-child(3)'))
        actions.context_click().send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        self.assertTrue(self.driver.is_element_present('.alert-danger'))
        self.assertEqual(self.driver.find_element_by_css_selector('.messages').text, 'PERMISSION DENIED')
