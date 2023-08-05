import urllib, hashlib
from hashlib import md5
from django import template
from django.conf import settings as conf
from sorl.thumbnail import get_thumbnail

register = template.Library()

# We call it avatar_url instead of gravatar_url so if we change services in the
# future it's just a change of the tag.
@register.simple_tag
def gravatar2(email, size=50, rating='g', default=None):
    """
    Returns a gravatar url.

    Example tag usage: {% gravatar user.email 80 "g" %}

    :Parameters:
       - `email`: the email to send to gravatar.
       - `size`: optional YxY size for the image.
       - `rating`: optional rating (g, pg, r, or x) of the image.
       - `default`: optional default image url or hosted image like wavatar.
    """
    # Verify the rating actually is a rating accepted by gravatar
    rating = rating.lower()
    ratings = ['g', 'pg', 'r', 'x']
    if rating not in ratings:
        raise template.TemplateSyntaxError('rating must be %s' % (
            ", ".join(ratings)))
    # Create and return the url
    hash = md5(email).hexdigest()
    url = 'http://www.gravatar.com/avatar/%s?s=%s&r=%s' % (
        hash, size, rating)
    if default:
        url = "%s&d=%s" % (url, default)
        
    return """<img class="thumbnail" src="%s" width="%s" height="%s" alt="gravatar" class="gravatar" border="0" />""" % (url, size, size)

@register.simple_tag
def gravatar(email):
    """
    Simply gets the Gravatar for the commenter. There is no rating or
    custom "not found" icon yet. Used with the Django comments.
    
    If no size is given, the default is 48 pixels by 48 pixels.
    
    Template Syntax::
    
        {% gravatar comment.user_email [size] %}
        
    Example usage::
        
        {% gravatar comment.user_email 48 %}
    
    """
    
    url = "http://www.gravatar.com/avatar.php?"
    url += urllib.urlencode({
        'gravatar_id': hashlib.md5(email).hexdigest(), 
        'size': conf.GRAVATAR_DEFAULT_SIZE,
        'default':  conf.GRAVATAR_DEFAULT_IMAGE
    })
    
    #return url
    return """<img src="%s" width="%s" height="%s" alt="gravatar" class="gravatar" border="0" />""" % (url, conf.GRAVATAR_DEFAULT_SIZE, conf.GRAVATAR_DEFAULT_SIZE)
