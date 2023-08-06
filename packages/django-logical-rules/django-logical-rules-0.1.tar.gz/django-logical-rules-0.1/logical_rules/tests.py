"""
    Unittests for the rules engine
"""
from django.test import TestCase
from django.test.client import Client

import sys, os, random

class TestRules(TestCase):

    def setUp(self):
        pass
        
    def testRuleEngine(self):
        """
            Test the Pizza rule
        """
        from django.contrib.auth.models import User
        u = User(username='tester')
        u.set_password('tester')
        u.save()
        c = Client()
        c.login(username='tester', password='tester')

        url = '/rules/order_pizza/cheese/20/' 
        response = c.get(url)
        self.assertEqual(response.status_code, 404)

        url = '/rules/order_pizza/pepperoni/10/' 
        response = c.get(url)
        self.assertEqual(response.status_code, 404)

        url = '/rules/order_pizza/olives/10/' 
        response = c.get(url)
        self.assertEqual(response.status_code, 404)

        url = '/rules/order_pizza/cheese/10/' 
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
