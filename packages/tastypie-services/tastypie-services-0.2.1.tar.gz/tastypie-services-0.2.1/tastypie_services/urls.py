from django.conf import settings

from tastypie.api import Api

from services import ErrorResource, SettingsResource, StatusResource

# Note: if you use this, errors might not get handled the way you want.
services = Api(api_name='services')
services.register(ErrorResource())
if getattr(settings, 'CLEANSED_SETTINGS_ACCESS', False):
    services.register(SettingsResource())
services.register(StatusResource())
