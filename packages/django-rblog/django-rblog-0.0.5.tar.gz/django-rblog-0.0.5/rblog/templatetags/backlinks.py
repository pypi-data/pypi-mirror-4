# -*- coding: utf-8 -*-

from django import template
import urllib2

from django.conf import settings as conf
from django.contrib.sites.models import Site

register = template.Library()

@register.inclusion_tag('elements/backlinks_list.html')
def backlinks_list():
    OpenInNewWindow = "1"
    BLKey = conf.KEY_BACKLINKS
    current_site = Site.objects.get(id=conf.SITE_ID)
    myurl = "http://"+current_site.domain

    QueryString = "LinkUrl=" + myurl
    QueryString = QueryString + "&Key=" + BLKey
    QueryString = QueryString + "&OpenInNewWindow=" + OpenInNewWindow

    req = urllib2.Request('http://www.backlinks.com/engine.php?' + QueryString)
    try:
        resp = urllib2.urlopen(req)
    except HTTPError, e:
        print e.code
        print e.read()

    output_code = '<ul class="interesting_links">' + resp.read() + '</ul>'
    
    edits = [('color: #000000; font-size: 10px; font-family: verdana; ', ''),
                ('border: 0px solid #FFFFFF; ', ''),
                ('<a ', '<li><a '),
                ('</a>', '</a></li>')]
    for search, replace in edits:
        output_code = output_code.replace(search, replace)

    return {
        'links': output_code
    }

"""
Template:
{% load cache %}

{% cache 21600 backlinks %}
{{ links|safe }}
{% endcache %}
"""
