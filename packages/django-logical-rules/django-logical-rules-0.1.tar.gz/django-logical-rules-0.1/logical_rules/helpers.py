import sys

def import_rules(app):
    from django.utils.importlib import import_module
    import imp
    import sys

    try:
        app_path = import_module(app).__path__
    except AttributeError:
        return None

    try:
        imp.find_module('rules', app_path)
    except ImportError:
        return None

    module = import_module('%s.rules' % app)
    return module

def autodiscover():
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        import_rules(app)
