# -*- coding: utf-8 -*-

from django import template
from django.utils.translation import ugettext as _
from rforum import utils

register = template.Library()

class EsModerador(template.Node):
    def __init__(self, usuario, topicslug):
        # Pasamos las variables a render
        self.usuario = template.Variable( usuario )
        self.topicslug = template.Variable( topicslug )
        
    def render(self, context):
        # Comprobamos lo que valen en su contexto
        usuario = self.usuario.resolve( context )
        topicslug = self.topicslug.resolve( context )

        # Seguimos con la lógica del filtro
        if utils.es_moderador(usuario, topicslug):
            return True
        else:
            return False
        

@register.tag
def es_moderador(parser, token):
    """
    Custom Tag que comprueba si es moderador o no, llama a la class EsModerador y
    devuelve True o False
    """
    try:
        tag_name, usuario, topicslug = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    return EsModerador(usuario, topicslug)
