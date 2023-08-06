from django.conf import settings

methods = { 'test': 'quickapi.views.test' }

QUICKAPI_DEFINED_METHODS = getattr(settings, 'QUICKAPI_DEFINED_METHODS', methods)
QUICKAPI_INDENT = getattr(settings, 'QUICKAPI_INDENT', 2)
