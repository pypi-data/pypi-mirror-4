from django.conf import settings
from django.db.models.loading import load_app
from django.test import TestCase
from django.template import Template, Context

import logical_rules

import sys

class TemplateTagTest(TestCase):
    def setUp(self):
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS.append('logical_rules.tests.test_app')
        load_app('logical_rules.tests.test_app')

    def tearDown(self):
        #logical_rules.site.unregister_all()
        settings.INSTALLED_APPS = self.old_INSTALLED_APPS

    def test_tag(self):
        logical_rules.helpers.autodiscover()
        content = (
                    "{% load logical_rules_tags %}"
                    "This is a {% testrule test_is_pizza 'pizza' %}test{% endtestrule %}"
                    "{% testrule test_is_pizza 'calzone' %}So is this...{% endtestrule %}"
                )
        expected = "This is a test"
        r = Template(content).render(Context({}))
        self.assertEqual(expected, r)
