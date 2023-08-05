from django.conf.urls import patterns, url


urlpatterns = patterns('polls.views',
    url(r'^poll/$', 'list'),
    url(r'^poll/(?P<poll_id>\d+)$', 'detail'),
)