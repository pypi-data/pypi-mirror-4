# -*- coding: utf-8 -*-

from django import template
from django.utils.translation import ugettext as _
import datetime
import rblog.models as mymodels

register = template.Library()

@register.filter
def split_first(cadena,arg):
    """
    Custom Filter que se encarga de hacer un split por arg y hardcodear un
    readmore, no se usa porque no se admite translate de la cadena, en su
    defecto se usa el custom tag split_one de abajo.
    """
    if not arg in cadena:
        return cadena
    return cadena.split(arg)[0] + '<a href="#">' + u'leer más' + '</a>'


class SplitOne(template.Node):
    
    """
    Clase que se encarga de coger un objeto cadena y hacerle un split para
    ver si hace falta ponerle un readmore o no.
    """
    
    def __init__(self, cadena, readmore):
        self.cadena = template.Variable( cadena )
        self.readmore = template.Variable( readmore )
        
    def render(self, context):
        cadena = self.cadena.resolve( context )
        argumento = '[@MORE@]'
        readmore = self.readmore.resolve( context )

        if not argumento in cadena.text:
            return cadena.text
        return cadena.text.split(argumento)[0] + '<div class="row"><div style="text-align: right"><div class="btn small primary"><a style="font-size: 14px;color: #fff; text-decoration: none;" title="' + readmore + '" href="/' + cadena.slug + '.html">' + readmore + '</a></div></div></div>'

@register.tag
def split_one(parser, token):
    """
    Custom Tag que llama a SplitOne() para hacerle (o no) split por [@MORE@] y
    mostrar un readmore o no.
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, cadena, readmore = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    return SplitOne(cadena, readmore)


@register.inclusion_tag('elements/archive.html', takes_context = True)
def archive(context):
    """
    Función que genera el html del archivo
    """
    first_post = mymodels.Post.objects.all().filter(status=1).order_by('creation_date')[0]

    year_ini = int(first_post.creation_date.strftime("%Y"))
    year_hoy = datetime.datetime.now().year
    mes_hoy = datetime.datetime.now().month
    meses = [_('Enero'), _('Febrero'), _('Marzo'), _('Abril'), _('Mayo'), _('Junio'), _('Julio'), _('Agosto'), _('Septiembre'), _('Octubre'), _('Noviembre'), _('Diciembre')] 
    years = range(year_ini, year_hoy+1)

    return {
        'years': years,
        'meses': meses,
        'year_hoy': year_hoy,
    }


