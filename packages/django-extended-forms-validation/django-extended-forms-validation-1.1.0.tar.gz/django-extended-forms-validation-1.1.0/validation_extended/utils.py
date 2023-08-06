import os
import importlib
import inspect

from django.conf import settings
from .validation import Validator


def get_all_validators():
    current_app = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    apps = filter(lambda app: not ('django' in app or app == current_app), settings.INSTALLED_APPS)
    validators = {}

    for appname in apps:
        app = importlib.import_module(appname)
        if hasattr(app, 'validators'):
            for name, cls in inspect.getmembers(app.validators):
                if inspect.isclass(cls) and issubclass(cls, Validator):
                    if not cls == Validator:
                        validators[name] = cls
    return validators
