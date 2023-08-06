# -*- coding: utf-8 -*-

import datetime
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib import messages
import models as mymodels
import forms as myforms
from tagging.models import Tag, TaggedItem
from django.conf import settings as conf
from django.views.generic import ListView, DetailView
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse

from disqusapi import DisqusAPI
from disqusapi import Paginator
from django.http import HttpResponse

class MetaSidebar():
    """Clase de la cual heredan las demas (para sideber por ejemplo)"""

    def __init__(self):
        pass

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
        current_site = get_current_site(self.request)
        current_url = reverse('app_blog-post-detail', kwargs={'slug': self.kwargs['slug']})
        # Si esta activado DISQUS_SYNC rellenamos el thread_id vía API
        if conf.DISQUS_SYNC:
            if not self.obj.thread_id:
                try:
                    print 'link:http://'+current_site.domain+current_url
                    api = DisqusAPI(conf.DISQUS_API_SECRET, conf.DISQUS_API_PUBLIC)
                    dq_response = api.threads.details(forum=conf.DISQUS_WEBSITE_SHORTNAME, thread='link:http://'+current_site.domain+current_url)
                    self.obj.thread_id = dq_response['id']
                except:
                    pass
                try:
                    print 'link:http://www.'+current_site.domain+current_url
                    api = DisqusAPI(conf.DISQUS_API_SECRET, conf.DISQUS_API_PUBLIC)
                    dq_response = api.threads.details(forum=conf.DISQUS_WEBSITE_SHORTNAME, thread='link:http://www.'+current_site.domain+current_url)
                    self.obj.thread_id = dq_response['id']
                except:
                    pass
        self.obj.save()
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        comments = mymodels.Comments.objects.filter(thread_id=self.obj.thread_id)
        context.update({
            'title': self.obj.title,
            'comments': comments,
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


class AJAXArchive(ListView):

    context_object_name = "resultado"
    template_name = "rblog/archive.html"
    model = mymodels.Post

    def get_context_data(self, **kwargs):
        context = super(AJAXArchive, self).get_context_data(**kwargs)

        first_post = mymodels.Post.objects.all().filter(status=1).order_by('creation_date')[0]
        year_ini = int(first_post.creation_date.strftime("%Y"))
        year_hoy = datetime.datetime.now().year
        mes_hoy = datetime.datetime.now().month
        meses = [_('Enero'), _('Febrero'), _('Marzo'), _('Abril'), _('Mayo'), _('Junio'), _('Julio'), _('Agosto'), _('Septiembre'), _('Octubre'), _('Noviembre'), _('Diciembre')]
        years = range(year_ini, year_hoy+1)

        results = dict()
        for j in range(year_ini, year_hoy+1):
            for i in range(1,13):
                num = mymodels.Post.objects.filter(
                    creation_date__year=j,
                    creation_date__month=i).count()
                results[j, i] = num

        context.update({
            'first_post': first_post,
            'year_ini': year_ini,
            'mes_hoy': mes_hoy,
            'meses': meses,
            'years': years,
            'year_hoy': year_hoy,
            'results': results,
        })
        return context

def cronAddDisqusComments(request, id=''):
    if conf.DISQUS_SYNC:
        last_comment = mymodels.Comments.objects.all().order_by('-date')
        last_date_imported='2003-04-24 13:25:09'
        if last_comment:
            last_date_imported=str(last_comment[0].date).replace('+00:00','')
        print last_date_imported
        try:
            api = DisqusAPI(conf.DISQUS_API_SECRET, conf.DISQUS_API_PUBLIC)
            for result in api.forums.listPosts(forum=conf.DISQUS_WEBSITE_SHORTNAME, limit='100', order='asc', since=last_date_imported):
                if not mymodels.Comments.objects.filter(comment_id=result['id']):
                    newcomment = mymodels.Comments.objects.create(comment_id=result['id'], date=result['createdAt'].replace('T',' '))
                    newcomment.thread_id = result['thread']
                    newcomment.forum_id = conf.DISQUS_WEBSITE_SHORTNAME
                    newcomment.body = result['message']
                    newcomment.author_name = result['author']['name']
                    newcomment.author_url = result['author']['url']
                    newcomment.author_email = result['author']['emailHash']
                    newcomment.save()
        except:
            pass

    output = "done"
    return HttpResponse(output)



