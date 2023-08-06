from django.conf import settings
#from django.core.management import call_command
from django.db.models.loading import load_app
from django.test import TestCase

import logical_rules

import sys

class RulesTest(TestCase):
    def setUp(self):
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS.append('logical_rules.tests.test_app')
        load_app('logical_rules.tests.test_app')
        #call_command('syncdb', verbosity=0, interactive=False)

    def tearDown(self):
        #logical_rules.site.unregister_all()
        settings.INSTALLED_APPS = self.old_INSTALLED_APPS
            
    def test_rules(self):
        logical_rules.helpers.autodiscover()
        self.assertTrue(logical_rules.site.is_registered('test_is_pizza'))
        self.assertTrue(logical_rules.site.test_rule('test_is_pizza', "pizza"))
        self.assertFalse(logical_rules.site.test_rule('test_is_pizza', "hamburger"))
