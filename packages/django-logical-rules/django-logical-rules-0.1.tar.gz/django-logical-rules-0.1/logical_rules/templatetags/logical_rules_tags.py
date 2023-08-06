from django import template

import logical_rules
import sys

register = template.Library()

class RuleTestNode(template.Node):
    """
    Shows content if the rule passes
    
    Usage:

    {% testrule rule_name rule_arg1 rule_arg2 %}
        Show this?
    {% endtestrule %}

    """
    child_nodelists = ('nodelist_true', 'nodelist_false')

    def __init__(self, rule_name, params, nodelist_true, nodelist_false):
        self.rule_name = rule_name
        self.params = params
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false

    def render(self, context):
        evaluated_params = []
        for p in self.params:
            v = template.Variable(p).resolve(context)
            evaluated_params.append(v)
        # @todo catch an exception here and just treat as false if rule is missing
        if logical_rules.site.test_rule(self.rule_name, *evaluated_params):
            return self.nodelist_true.render(context)
        return self.nodelist_false.render(context)
        #return "Rule: %s %s" % (self.rule_name, self.params)

@register.tag
def testrule(parser, token):

#    args = token.contents.split()
#    if len(args) < 2:
#        raise TemplateSyntaxError("'testrule' tag requires at least a rule name.")
#
#    rule_name = args[1]
#    params = []
#    if len(args) > 2:
#        params = args[2:]
#
#    nodelist = parser.parse(('endtestrule',))
#    parser.delete_first_token()
#    return RuleTestNode(rule_name, params, nodelist)

    args = token.contents.split()
    if len(args) < 2:
        raise TemplateSyntaxError("'testrule' tag requires at least a rule name.")

    rule_name = args[1]
    params = []
    if len(args) > 2:
        params = args[2:]

#    bits = token.split_contents()[1:]
#    var = template.defaulttags.TemplateIfParser(parser, bits).parse()
    nodelist_true = parser.parse(('else', 'endtestrule'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endtestrule',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return RuleTestNode(rule_name, params, nodelist_true, nodelist_false)
