from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.importlib import import_module
from django.views import debug

from tastypie import fields
from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import Resource
from tastypie.serializers import Serializer


class TestError(Exception):
    pass


class ServiceResource(Resource):

    class Meta:
        always_return_data = True
        serializer = Serializer(formats=['json'])


class ErrorResource(ServiceResource):

    class Meta(ServiceResource.Meta):
        list_allowed_methods = ['get']
        resource_name = 'error'

    def obj_get_list(self, request=None, **kwargs):
        # All this does is throw an error. This is used for testing
        # the error handling on dev servers.
        raise TestError('This is a test.')


class SettingsObject(object):

    def __init__(self, name):
        self.pk = name
        cleansed = debug.get_safe_settings()
        self.cleansed = debug.cleanse_setting(name, cleansed[name])


class SettingsResource(ServiceResource):
    value = fields.CharField(readonly=True, attribute='cleansed', null=True)
    key = fields.CharField(readonly=True, attribute='pk')

    class Meta(ServiceResource.Meta):
        list_allowed_methods = ['get']
        allowed_methods = ['get']
        resource_name = 'settings'

    def get_resource_uri(self, bundle):
        return reverse('api_dispatch_detail',
                        kwargs={'api_name': 'services',
                                'resource_name': 'settings',
                                'pk': bundle.obj.pk})

    def obj_get(self, request, **kwargs):
        pk = kwargs['pk']
        cleansed = debug.get_safe_settings()
        if pk not in cleansed:
            raise ImmediateHttpResponse(response=http.HttpNotFound())
        return SettingsObject(pk)

    def obj_get_list(self, request, **kwargs):
        keys = sorted(debug.get_safe_settings().keys())
        return [SettingsObject(k) for k in keys]


class StatusError(Exception):
    pass


class StatusObject(object):
    """
    This is an object to override to check whatever you'd like to check.
    By default it does nothing and just raises an error. You might want to
    subclass and override, test_cache, test_db etc...

    Each test should set the corresponding attribute to True or False.
    """
    pk = 'status'
    cache = False
    db = False
    # Note: we set this to True by default because if you've got to this
    # point, it's likely that your settings are just fine.
    settings = True

    def __repr__(self):
        values = ['%s: %s' % (k, v) for k, v in self.checks]
        return '<Status: %s>' % ', '.join(values)

    @property
    def checks(self):
        return [(k, getattr(self, k)) for k in ['cache', 'db', 'settings']]

    def test_cache(self):
        """
        Check the connection to your cache.
        """
        raise NotImplementedError

    def test_db(self):
        """
        Check the connection to your database.
        """
        raise NotImplementedError

    def test_settings(self):
        """
        Test any application specific settings that you might want to
        confirm are set.
        """
        raise NotImplementedError

    def test(self):
        self.test_cache()
        self.test_db()
        self.test_settings()
        return all([c[1] for c in self.checks])


class StatusResource(ServiceResource):
    cache = fields.BooleanField(readonly=True, attribute='cache')
    db = fields.BooleanField(readonly=True, attribute='db')
    settings = fields.BooleanField(readonly=True, attribute='settings')

    class Meta(ServiceResource.Meta):
        list_allowed_methods = ['get']
        allowed_methods = ['get']
        resource_name = 'status'

    def obj_get(self, request, **kwargs):
        print getattr(settings, 'SERVICES_STATUS_MODULE',
                         'services.services')

        client = getattr(settings, 'SERVICES_STATUS_MODULE',
                         'services.services')
        obj = import_module(client).StatusObject()
        if not obj.test():
            raise StatusError(str(obj))
        return obj

    def obj_get_list(self, request=None, **kwargs):
        return [self.obj_get(request, **kwargs)]
