# -*- coding: utf-8 -*-

import datetime
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib import messages
import models as mymodels
import forms as myforms
from tagging.models import Tag, TaggedItem
from django.conf import settings as conf
from django.views.generic import ListView, DetailView

#import json
from django.http import HttpResponse

class MetaSidebar():
    """Clase de la cual heredan las demas (para sideber por ejemplo)"""

    def __init__(self):
        pass

class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        #return json.dumps(context)
        return context



class BlogIndexView(MetaSidebar, ListView):

    template_name = "rblog/index.html"
    context_object_name = "myposts"
    paginate_by = 20

    def __init__(self):
        MetaSidebar.__init__(self)

    def get_queryset(self):
        return mymodels.Post.objects.all().filter(status=1).order_by('-creation_date')

    def get_context_data(self, **kwargs):
        context = super(BlogIndexView, self).get_context_data(**kwargs)
        context.update({
            'title': _('Blog'),
            'description': conf.SITE_DESCRIPTION,
        })
        return context

class PostDetailView(MetaSidebar, DetailView):

    template_name = "rblog/detail.html"
    context_object_name = "mypost"

    def __init__(self):
        MetaSidebar.__init__(self)

    def get_object(self):
        self.obj = get_object_or_404(mymodels.Post, slug=self.kwargs['slug'], status=1)
        self.obj.hits = self.obj.hits + 1
        self.obj.save()
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context.update({
            'title': self.obj.title,
        })
        return context


class PostsWithTag(MetaSidebar, ListView):

    template_name = "rblog/index.html"
    context_object_name = "myposts"
    paginate_by = 20

    def __init__(self):
        MetaSidebar.__init__(self)

    def get_queryset(self):
        query_tag = Tag.objects.get(name=self.kwargs['tag'])
        myposts = TaggedItem.objects.get_by_model(mymodels.Post, query_tag)
        return myposts.all().filter(status=1).order_by('-creation_date')

    def get_context_data(self, **kwargs):
        context = super(PostsWithTag, self).get_context_data(**kwargs)
        context.update({
            'title': _('Tag') + " " + self.kwargs['tag'],
            'description': _('Bunch of posts about tag') + ": " + self.kwargs['tag'],
            'tag': self.kwargs['tag'],
        })
        return context


class PostsByDate(MetaSidebar, ListView):

    template_name = "rblog/index.html"
    context_object_name = "myposts"
    paginate_by = 20

    def __init__(self):
        MetaSidebar.__init__(self)

    def get_queryset(self):
        archive = str(self.kwargs['month']) + '.' + str(self.kwargs['year'])
        return mymodels.Post.objects.all().filter(status=1,
                creation_date__month=self.kwargs['month'],
                creation_date__year=self.kwargs['year']).order_by('-creation_date')

    def get_context_data(self, **kwargs):
        context = super(PostsByDate, self).get_context_data(**kwargs)
        context.update({
            'title': _('Archive') + " " + str(self.kwargs['month']) + '.' + str(self.kwargs['year']),
            'description': _('Bunch of posts on the date') + ": " + str(self.kwargs['month']) + '.' + str(self.kwargs['year']),
            'archive': str(self.kwargs['month']) + '.' + str(self.kwargs['year']),
            'month': str(self.kwargs['month']),
            'byear': str(self.kwargs['year']),
        })
        return context


class AJAXPostsYear(JSONResponseMixin, ListView):

    context_object_name = "resultado"
    model = mymodels.Post

    def get_context_data(self, **kwargs):
        """
        Agregamos al context la variable json_data, que contiene una
        lista de diccionarios con valores para cargar luego, via ajax
        en una plantilla, usando javascript
        """
        context = super(AJAXPostsYear, self).get_context_data(**kwargs)

        results = {}
        re = "{"
        for i in range(1,13):
            num = mymodels.Post.objects.filter(
                creation_date__year=self.request.GET.get('year', datetime.datetime.now().year),
                creation_date__month=i).count()
            results[i] = num
            re = re + '"' + str(i) + '": ' + str(num) + ','
        re = re[:-1]
        re = re + "}"
        return re
