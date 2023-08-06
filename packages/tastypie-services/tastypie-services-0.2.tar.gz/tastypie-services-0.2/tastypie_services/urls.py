from django.conf import settings

from tastypie.api import Api

from services import ErrorResource, SettingsResource, StatusResource

services = Api(api_name='services')
services.register(ErrorResource())
if getattr(settings, 'CLEANSED_SETTINGS_ACCESS', False):
    services.register(SettingsResource())
services.register(StatusResource())
