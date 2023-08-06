import sys

class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class RuleRegistry(object):
    def __init__(self):
        self._registry = {}
    
    def register(self, rule_name, rule, **options):
        if rule_name not in self._registry:
            self._registry[rule_name] = rule
        else:
            raise AlreadyRegistered("The rule %s is already registered" % rule_name)

    def unregister(self, rule_name):
        if rule_name in self._registry:
            del self._registry[rule_name]
        else:
            raise NotRegistered("The rule %s is not registered" % rule_name)
        
    def unregister_all(self):
        self._registry = {}

    def unregister_app(self, app_name):
        """ @Todo: This would be cool """
        raise NotImplementedError

    def is_registered(self, rule_name):
        return self._registry.has_key(rule_name)

    def get_rule(self, rule_name):
        try:
            return self._registry[rule_name]
        except KeyError:
            raise NotRegistered("Rule %s has not been registered" % rule_name)

    def test_rule(self, rule_name, *args):
        rule = self.get_rule(rule_name)
        return rule(*args)
