# -*- coding: utf-8 -*-
import models as mymodels
import utils
from django.shortcuts import get_object_or_404, render_to_response
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

class IsModerator(object):

    def process_view(self, request,view_func,view_args,view_kwargs):

        """
        Debug time: Aquí paramos el código para ver las variables de entorno
                    que nos encontramos, tenemos varias opciones:
                    l - Nos muestra el número de linea en la que estamos
                    n - Salta a la siguiente linea de ejecución
                    p dir(var) - Muestra todos los métodos de la variable dir
                    var - Es como hacer un "print" de la variable, muestra su
                          contenido.
        """
        #import pdb; pdb.set_trace()

        """ Devuelve True o False """

        #print request
        #print request.user
        #print view_func.__name__
        #print view_kwargs['slug']

        functionlist = ['PostUpdate', 'PostDelete', 'TopicAction', 'TopicDelete']
        if view_func.__name__ in functionlist:

        try:
            if any(view_func.__name__ in s for s in functionlist):
                if view_kwargs['topicslug']:
                    if utils.es_moderador(request.user, view_kwargs['topicslug']):
                        return None
                    else:
                        messages.add_message(request, messages.ERROR, _('No eres moderador, cuidado con lo que haces'))
                        return redirect('account_profile')
        except:
            return None

        return None
