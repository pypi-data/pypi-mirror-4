# -*- coding: utf-8 -*-

from django import template
from django.utils.translation import ugettext as _
import rforum.models as mymodels

register = template.Library()

class Rank(template.Node):
    def __init__(self, usuario, numposts):
        # Pasamos las variables a render
        self.usuario = template.Variable( usuario )
        self.numposts = template.Variable( numposts )
        
    def render(self, context):
        # Comprobamos lo que valen en su contexto
        usuario = self.usuario.resolve( context )
        numposts = self.numposts.resolve( context )

        # Seguimos con la lógica del filtro
        therank = mymodels.Rank.objects.get(limit_from__lte=numposts, limit_to__gte=numposts)
        print therank
        return therank

@register.tag
def rank(parser, token):
    """
    Custom Tag que comprueba si es moderador o no, llama a la class EsModerador y
    devuelve True o False
    """
    try:
        tag_name, usuario, numposts = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    return Rank(usuario, numposts)
