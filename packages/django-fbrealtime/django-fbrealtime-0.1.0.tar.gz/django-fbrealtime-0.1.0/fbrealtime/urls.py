from django.conf.urls import patterns, include, url

urlpatterns = patterns('fbrealtime.views',
    url(r'fbrealtime/callback/$', 'callback'),
)
