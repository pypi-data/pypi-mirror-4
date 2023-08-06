from django.contrib import admin

from .models import Feed, FeedItem, Category


class FeedItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'feed', 'read')


class FeedAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'category', 'get_unread_count', 'last_update')
    readonly_fields = ['last_update', 'title']
    save_on_top = True

admin.site.register(Feed, FeedAdmin)
admin.site.register(FeedItem, FeedItemAdmin)
admin.site.register(Category)