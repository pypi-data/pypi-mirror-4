=================
django-fbrealtime
=================

A simiple django app to integrate with facebook realtime updates.


Requirements
============
django 1.4 or later

Installation
============

1. ''pip install django-fbrealtime''

2. Add 'fbrealtime' to your list of INSTALLED_APPS in settings.py

3. Add FACEBOOK_API_SECRET FACEBOOK_VERIFY_TOKEN to settings.py

4. Add url(r'', include('fbrealtime.urls')), to URLConf

Use
===
Subscribe to fbrealtime.signals.data_imported signal

    from django.dispatch import receiver
    import fbrealtime.signals.fb_update

    @recciver(fbrealtime.signals.fb_update)
    def fb_update_handler(sender, **kwargs):
        # update is a dictionary of updates from facebook
        update = kwargs.get('update') 
        ...


