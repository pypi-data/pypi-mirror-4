from django.db.models.query import QuerySet
from django.db.models import Manager


class FeedItemQuerySet(QuerySet):
    def my_feed_items(self, user):
        return self.filter(feed__user=user)

    def category(self, category_slug):
        return self.filter(feed__category__slug=category_slug)

    def un_read(self):
        return self.filter(read=False)

    def read(self):
        return self.filter(read=True)


class FeedItemManager(Manager):
    def get_query_set(self):
        return FeedItemQuerySet(self.model, using=self._db)

    def category(self, category_slug):
        return self.get_query_set().category(category_slug)

    def my_feed_items(self, user):
        return self.get_query_set().my_feed_items(user)

    def un_read(self):
        return self.get_query_set().un_read()

    def read(self):
        return self.get_query_set().read()


