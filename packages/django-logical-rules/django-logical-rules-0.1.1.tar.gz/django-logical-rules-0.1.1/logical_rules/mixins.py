from django.core import exceptions
from django.http import HttpResponseRedirect
from django.contrib import messages

import logical_rules


class RulesMixin(object):
    """
        A mixin that will apply certain rules before a view
        is fully executed

        Rules are defined in a list of dictionary objects such as the following:

            [{
                'name': 'my_rule',
                'param_callbacks':
                    [
                        ('user', "request.user")
                    ],
                "redirect_url": "/account/"
            }]

        Optional (though not very often)
        `callback_parameters` are callback methods or properties to get the value of the parameters
        
        Optional params:
        `redirect_url` otherwise a 403 is raised
        `response_callback` it executes a method on the class that returns a response
        `message` issues a message to the user along with the permissiond denied error
        `message_level` defaults to django.contrib.messages.ERROR

        Typical implementation might look like this:

            class MyView(RulesMixin, TemplateView):

                def update_logical_rules(self):
                    super(MyView, self).update_logical_rules()
                    self.add_logical_rule({
                                    'name': 'my_rule',
                                    'param_callbacks':
                                        [('user', "request.user")],
                                    "redirect_url": "/account/"
                                    })

        For now this only covers GET and POST requests
    """
    def get(self, request, *args, **kwargs):
        # Catch any rules before get
        response = self._test_logical_rules()
        if response:
            return response
        return super(RulesMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Catch any rules before post
        response = self._test_logical_rules()
        if response:
            return response
        return super(RulesMixin, self).post(request, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        """
            Sets up the class and calls update_logical_rules to get all rules
            from child classes
        """
        super(RulesMixin, self).__init__(*args, **kwargs)
        self._logical_rules = []
        self.update_logical_rules()

    def update_logical_rules(self):
        pass

    def add_logical_rule(self, rule_dict):
        """
            Adds a logical rule to the class
        """
        self._logical_rules.append(rule_dict)

    def _test_logical_rules(self):
        """
            Run all the rules and return a response object if necessary
        """
        for rule in self._logical_rules:
            response = self._test_logical_rule(rule)
            if response:
                return response

    def _test_logical_rule(self, rule):
        """
            Run a specific rule and return a response if necessary

            @todo - it would be nice to change this so it can handle properties
            as well as methods on the class
        """

        # get parameters
        args = []
        for k, v in rule['param_callbacks']:
            arg = getattr(self, v)
            args.append(arg())

        # run rule
        if not logical_rules.site.test_rule(rule['name'], *args):
            if 'redirect_url' in rule.keys():
                return HttpResponseRedirect(rule['redirect_url'])
            if 'response_callback' in rule.keys():
                callback = getattr(self, rule['response_callback'])
                return callback()
            if 'message' in rule.keys():
                message_level = messages.ERROR
                if 'message_level' in rule.keys():
                    message_level = rule['message_level']
                messages.add_message(self.request, message_level, rule['message'])    
            raise exceptions.PermissionDenied
        return None

    ## Helper Methods
    def get_request_user(self):
        """
            A quick helper function to make self.request.user available as a callback
        """
        return self.request.user
