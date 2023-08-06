from django.views.generic import ListView, DetailView
from django.conf import settings

from infuse.auth.permissions import LoginRequiredMixin

from .models import Feed, FeedItem, Category
from .forms import AddFeedForm


class FeedList(LoginRequiredMixin, ListView):
    """
    Show the feed list for the logged in user.
    @todo - need to protect ti with logged in user
    """
    template_name = 'feedme/feed_list.html'
    context_object_name = 'feed_items'

    def update_feeds(self, user):
        for feed in Feed.objects.filter(user=user):
            feed.update()
        return True

    def get_queryset(self):
        # Update the feed on page load..
        self.update_feeds(self.request.user)
        items = FeedItem.objects.my_feed_items(self.request.user).un_read()

        if self.kwargs.get('category', None):
            return items.category(self.kwargs.get('category'))

        if self.kwargs.get('feed_id', None):
            return items.filter(feed__id=self.kwargs.get('feed_id'))

        return items

    def get_context_data(self, **kwargs):
        context = super(FeedList, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['add_form'] = AddFeedForm()

        return context

