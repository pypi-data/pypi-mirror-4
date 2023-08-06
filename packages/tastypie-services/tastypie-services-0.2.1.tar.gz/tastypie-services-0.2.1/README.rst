A simple API end point that we've found useful for our Tastypie API services at
Mozilla.

Installation
------------

Install using pip::

        pip install tastypie-services

Note: version 2 renamed the lib from services to tastypie_services.

Configuration
-------------

Add to your urls::

        from tastypie_services.urls import services

        urlpatterns = patterns('',
                ...
                url(r'^', include(services.urls)),
        )

If you want to allow settings access, set::

        CLEANSED_SETTINGS_ACCESS = False

The actual server status is very specific to your server, so you need to create
a base class overriding the one in services. The tell the library where the
object is. For example::

        SERVICES_STATUS_MODULE = 'lib.services.resources'

Then in `lib.tastypie_services.resources`::

        from tastypie_services.services import StatusObject as Base

        class StatusObject(Base):

            def test_cache(self):
                cache.set('status', 'works')
                if cache.get('status') == 'works':
                        self.cache = True

See solitude for an example of this.
