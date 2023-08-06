from django.test import TestCase

from feedme.models import Feed, FeedItem


class FeedMeTestCase(TestCase):

    def test_update_feed(self):
        feed = Feed(url='http://derek.stegelman.com/blog/feed/')
        feed.save()
        feed.update(force=True)
        self.assertTrue(FeedItem.objects.all().count(), 10)

    def test_me(self):
        self.assertTrue(True, True)