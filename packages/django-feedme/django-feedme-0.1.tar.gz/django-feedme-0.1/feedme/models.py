import datetime

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from hadrian.utils.slugs import unique_slugify

import feedparser

from .managers import FeedItemManager


class Category(models.Model):
    name = models.CharField(max_length=250, blank=True)
    slug = models.SlugField(blank=True, null=True, editable=False)
    user = models.ForeignKey(User, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(Category, self).save(*args, **kwargs)

    @property
    def get_unread_count(self):
        return FeedItem.objects.my_feed_items(self.user).category(self.slug).un_read().count()


class Feed(models.Model):
    url = models.CharField(blank=True, max_length=450)
    title = models.CharField(blank=True, null=True, max_length=250)
    category = models.ForeignKey(Category, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    last_update = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.url

    def _get_title(self):
        parser = feedparser.parse(self.url)
        return parser.feed.title

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self._get_title()
        super(Feed, self).save(*args, **kwargs)
        if self.last_update is None:
            self.update(force=True)

    @property
    def get_unread_count(self):
        return FeedItem.objects.filter(feed=self).un_read().count()

    def _update_feed(self):
        # Update the last update field
        self.last_update = datetime.date.today()
        self.save()
        for item in feedparser.parse(self.url).entries[:10]:
            # Search for an existing item
            try:
                FeedItem.objects.get(title=item.title)
            except FeedItem.DoesNotExist:
                # Create it.
                feed_item = FeedItem(title=item.title, link=item.link, content=item.description, feed=self)
                feed_item.save()

    def _update_processor(self):
        if getattr(settings, 'FEED_UPDATE_CELERY', False):
            from .tasks import update_feed
            update_feed.delay(self)
            return True
        self._update_feed()
        return True

    def update(self, force=False):
        """ If we aren't forcing it
        and its not the same day, go ahead
        and update the feeds.
        """

        if force or not force and self.last_update < datetime.date.today():
            self._update_processor()
            return True

    @models.permalink
    def get_absolute_url(self):
        return ('feedme-feed-list-by-feed', (), {'feed_id': self.id})


class FeedItem(models.Model):
    title = models.CharField(max_length=350, blank=True)
    link = models.URLField(blank=True)
    content = models.TextField(blank=True)
    feed = models.ForeignKey(Feed, blank=True, null=True)
    read = models.BooleanField()

    objects = FeedItemManager()

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return self.title

