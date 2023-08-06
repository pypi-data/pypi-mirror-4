from django.conf.urls import patterns, include, url

from .views import FeedList
from .ajax import mark_as_read

urlpatterns = patterns('',
   url(r'^$', FeedList.as_view(), name="feedme-feed-list"),
   url(r'^by_category/(?P<category>[-\w]+)/$', FeedList.as_view(), name='feedme-feed-list-by-category'),
   url(r'^by_feed/(?P<feed_id>[-\w]+)/$', FeedList.as_view(), name='feedme-feed-list-by-feed'),
   url(r'^ajax/mark_as_read/$', mark_as_read, name='feedme-mark-as-read-ajax'),
   #url(r'^(?P<ethnicity>[-\w]+)/$', EateryList.as_view(), name='eatery-by-ethnicity'),
   #url(r'^eatery/(?P<slug>[-\w]+)/$', EateryDetail.as_view(), name="eatery-detail"),

   )
