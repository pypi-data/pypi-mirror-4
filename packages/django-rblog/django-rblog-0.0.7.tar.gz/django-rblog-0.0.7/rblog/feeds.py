from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from tagging.models import Tag, TaggedItem
from rblog.models import Post

from django.conf import settings as conf

class AllFeed(Feed):

    """
    Clase de feeds en general (http://dominio.com/feed/)
    Referencias:
    - http://docs.djangoproject.com/en/dev/ref/contrib/syndication/?from=olddocs
    - http://www.andrlik.org/writing/2007/aug/03/fun-with-django-feeds/
    """

    title = conf.SITE_TITLE
    link = "/"
    description = conf.SITE_DESCRIPTION

    def items(self):
        return Post.objects.all().filter(status=1).order_by('-creation_date')[:5]

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        return item.text

class TagFeed(Feed):

    """
    Clase de feeds para los tags (http://dominio.com/tag-elquesea/feed/)
    """

    title = conf.SITE_TITLE
    link = "/"
    description = conf.SITE_DESCRIPTION

    def get_object(self, request, tag):
        return Tag.objects.get(name=tag)
        
    def items(self, obj):
        myposts = TaggedItem.objects.get_by_model(Post, obj)
        myposts = myposts.all().filter(status=1).order_by('-creation_date')[:5]
        return myposts

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        return item.text
