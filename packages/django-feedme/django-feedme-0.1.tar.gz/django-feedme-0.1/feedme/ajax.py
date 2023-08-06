from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import FeedItem

@csrf_exempt
def mark_as_read(request):
    if request.method == "POST":
        feed_item = get_object_or_404(FeedItem, pk=request.POST.get('feed_item_id'))
        feed_item.read = True
        feed_item.save()

    return HttpResponse()
