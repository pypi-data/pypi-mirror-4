# -*- coding: utf-8 -*-

from django import template
from django.utils.translation import ugettext as _

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


@register.simple_tag
def archive():
    """
    Función que genera el html del archivo
    """
    
    year_ini = 2002
    import datetime    
    year_hoy = datetime.datetime.now().year
    mes_hoy = datetime.datetime.now().month
    meses = [_('Enero'), _('Febrero'), _('Marzo'), _('Abril'), _('Mayo'), _('Junio'), _('Julio'), _('Agosto'), _('Septiembre'), _('Octubre'), _('Noviembre'), _('Diciembre')] 
    
    cadena = '<ul>'
    for i in range(year_ini, year_hoy+1):
        cadena= cadena + '<li class="page_item"><a href="#">' + str(i) + '</a><ul>'
        if i==year_hoy:
            mmes=mes_hoy+1
        else:
            mmes=12+1
        for j in range(1,mmes):
            cadena = cadena + '<li class="page_item"><a href="/%s/%02d/">%s</a></li>' % (str(i), (j), meses[j-1])
        cadena = cadena + '</ul></li>'
    cadena = cadena + '</ul>'
    return cadena



@register.simple_tag
def archive2():
    """
    Función que genera el html del archivo en tabs
    """
    
    year_ini = 2002
    import datetime    
    year_hoy = datetime.datetime.now().year
    mes_hoy = datetime.datetime.now().month
    meses = [_('Enero'), _('Febrero'), _('Marzo'), _('Abril'), _('Mayo'), _('Junio'), _('Julio'), _('Agosto'), _('Septiembre'), _('Octubre'), _('Noviembre'), _('Diciembre')] 

    cadena = '<ul data-toggle="tab" class="nav nav-tabs">'
    for i in range(year_ini, year_hoy+1):
        myclass=""
        if i==year_hoy:
            myclass="active"
        cadena= cadena + '<li class="'+myclass+'"><a href="#'+str(i)+'">' + str(i) + '</a></li>'
    cadena = cadena + '</ul>'


    cadena = cadena + '<div class="tab-content">'
    for i in range(year_ini, year_hoy+1):
        hd=""
        if i==year_hoy:
            hd="active"
            mmes=mes_hoy+1
        else:
            mmes=12+1

        cadena = cadena + '<div class="tab-pane '+hd+'" id="'+str(i)+'">'
        cadena = cadena + """
<table class="zebra-striped">
    <thead>
	    <tr>
		    <th class="green header">DD</th>
		    <th class="blue header">Month</th>
		    <th class="yellow header">Year</th>
		    <th class="green header">Posts</th>
	    </tr>
    </thead>
    <tbody>"""

        for j in range(1,mmes):
            #cadena = cadena + """<li><a href="/%s/%02d/">%s</a></li>
            cadena = cadena + """<tr>
		    <td><img src="" alt="Descarga" title="Descarga"></td>
		    <td><a href="/%s/%02d/">%s</a></td>
		    <td><span>%s</span></td>
		    <td><span>1.50</span><span> GB</span></td>
	    </tr>"""  % (str(i), (j), meses[j-1], str(i))
        cadena = cadena + '</tbody></table></div>'
    cadena = cadena + '</div>'
    
    return cadena

















