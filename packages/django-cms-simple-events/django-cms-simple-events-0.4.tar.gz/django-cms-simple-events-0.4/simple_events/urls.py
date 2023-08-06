from django.conf.urls.defaults import *
from models import Event
from django.views.generic.dates import DateDetailView

urlpatterns = patterns('',
    url(r'^$', 'simple_events.views.events', name='events'),
    url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$',
            'simple_events.views.events_day', name="events_day"),
    url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[-\w]+)/$',
            'simple_events.views.events_detail', name="events_detail"),
)
