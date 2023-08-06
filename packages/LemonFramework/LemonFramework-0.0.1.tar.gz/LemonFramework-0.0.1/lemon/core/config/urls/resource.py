"""
This file is part of Lemon.

Lemon is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lemon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lemon. If not, see <http://www.gnu.org/licenses/>.


Copyright (c) 2012 Vicente Ruiz <vruiz2.0@gmail.com>
"""
import re

from lemon import http
from lemon.core.aspects import AspectType
from lemon.core.config.exceptions import (URLBadFormedException,
    InvalidConfigException)
from lemon.core.utils.imports import import_object
from lemon.renders.exceptions import RenderParamsException


class Resource(metaclass=AspectType):
    """Representa un recurso, accesible a través de URL. Dicho de otra forma,
    contiene toda la información necesaria para atender una URL concreta:
    controlador, renders, ..."""
    
    def __init__(self, pattern='^$', base=None, nested=False, **kwargs):
        """Crea un nuevo recurso. Para ello se utilizan los siguientes
        parámetros:
            ``pattern`` Patrón para el nivel actual dentro de la URL
            ``base`` Objeto de tipo Resource que está en el nivel superior
            ``nested`` Parámetro utilizado por ``get_urls`` para añadir la
                información necesaria para las suburls propias del controlador
            ``kwargs`` Parámetros opcionales:
                ``name`` Nombre del recurso
                ``priority`` Lista con la
                ``controller`` Controlador que atenderá la petición
                ``renders`` Conjunto de renders utilizados para esta petición
        """
        self.url = ''
        self.regexp = None
        self.base_regexp = None
        self.name = None
        self.priority = []
        self.controller = None
        self.renders = {}
        self.context_processors = []

        params = kwargs.copy()
        # Default base pattern
        base_url = '^/$'

        if base is not None:
            # Inherited aspects
            self.renders.update(base.renders)
            self.context_processors += base.context_processors
            # Base pattern to concatenate
            base_url = base.url or base_url

        # Preparing the pattern for this URL
        base_url = base_url if base_url[-1] != '$' else base_url[0:-1]
        pattern = pattern if pattern[0] != '^' else pattern[1:]
        # Avoid slash duplication
        if base_url[-1] == '/' and pattern[0] == '/':
            pattern = pattern[1:]

        self.url = base_url + pattern
        if self.url[-1] != '$':
            self.url += '$'
        try:
            self.regexp = re.compile(self.url)
        except re.error as error:
            raise URLBadFormedException(error)
        
        if nested:
            base_url = base_url
        else:
            base_url = self.url[:-1]
            
        self.base_regexp = re.compile(base_url + '(?P<extra_controller>.*)')

        # Getting the name
        self.name = params.pop('name', None)
        # Getting the priority
        self.priority = tuple(params.pop('priority', ()))
        # Getting the controller
        self._set_controller(params.pop('controller', None))
        # Getting local renders
        self._set_renders(params.pop('renders', {}))
        # Getting local context_processors
        self._set_context_processors(params.pop('context_processors', ()))
    
    def _set_controller(self, controller):
        if isinstance(controller, str):
            controller = import_object(controller)
        if callable(controller):
            controller = controller()
        
        self.controller = controller
    
    def _set_renders(self, renders):
        # Remove 'None' renders from this URL
        for mimetype, render in renders.items():
            if render is None:
                self.renders.pop(render, None)
        # Update with not 'None' renders
        self.renders.update(
            (mimetype, render) for mimetype, render in renders.items()
            if render is not None
        )

        for mimetype, render in self.renders.items():
            # Si es una cadema de texto, la importamos
            if isinstance(render, str):
                render = import_object(render)
            if callable(render):
                render = render()
            self.renders[mimetype] = render
    
    def _set_context_processors(self, context_processor_list):
        context_processors = []

        for context_processor in context_processor_list:
            # Si es una cadema de texto, la importamos
            if isinstance(context_processor, str):
                context_processor = import_object(context_processor)
            # Forzamos a que sea invocable
            if not callable(context_processor):
                raise InvalidConfigException(
                    'Context processor is not callable'
                )
            # Añadimos ``context_processor`` a la lista
            context_processors.append(context_processor)

        return tuple(context_processors)

    def __str__(self):
        return '(%s, %s)' % (
            self.url,
            self.name,
        )

    def is_resource(self):
        """
        Indica is un recurso es válido. Un recurso se considera válido si se
        puede acceder a él a través de una URL, o dicho de otra forma, si tiene
        un controlador asociado.
        """
        return self.controller is not None

    def get_urls(self):
        """
        Devuelve las URLs a través de las cuales se puede acceder al recurso.
        Esto viene determinado por el controlador. Lo habitual es que el
        controlador devuelva una sóla URL, aunque algunos controladores, como
        CrudController, pueden utilizar varias URLs.

        Si el recurso no es válido, es decir, no se puede acceder a él a través
        de una URL devolverá una lista vacía.
        """
        urls = []
        
        # Comprobamos que es un recurso válido, es decir, tiene un controlador
        if self.is_resource():
            # Obtenemos la lista de suburls que gestiona el controlador
            nested_urls = self.controller.get_urls()
            # Comprobamos si hay alguna suburl
            if len(nested_urls) > 0:
                # Recorremos las suburls (y sus nombres) gestionadas por el
                # controlador
                for nested_url, nested_name in nested_urls:
                    # Inicialmente, la url no tiene ningún nombre
                    name = None
                    # En caso de que el recurso actual tenga nombre, preparamos
                    # un nuevo nombre
                    if self.name:
                        # Si el controlador ha indicado un nombre ...
                        if nested_name:
                            # ... se genera el nombre como la composición
                            name = self.name + ':' + nested_name
                        else:
                            # ... si no, se utiliza el nombre original
                            name = self.name
                    # Creamos un nuevo recurso, basado en el recurso en el
                    # actual, indicado que es anidado
                    resource = Resource(
                        nested_url,
                        self,
                        nested=True,
                        name=name,
                        controller=self.controller,
                        priority=self.priority,
                        renders=self.renders,
                    )
                    # Añadimos el recurso a la lista de URLs a devolver
                    urls.append(resource)
            else:
                # En caso de que el controlador no gestione ninguna suburl, es
                # éste mismo recurso el único que se devuelve
                urls.append(self)
        
        return tuple(urls)
    
    def match(self, url):
        """
        Indica si este recurso se encarga de atender una determinada URL. Para
        que pueda atenderla, es necesario tener asociado un controlador y además
        que coincida con la expresión regular completa de la url.
        """
        return self.is_resource() and self.regexp.match(url)

    def attend(self, request):
        """
        Atiende una petición dirigida a este recurso y devuelve la respuesta
        oportuna. Puede lanzar las siguientes excepciones:
         - HttpResponseUnsupportedMediaType: el controlador no soporta el método
           solicitado.
         - HttpResponseNotFound: se ha invocado a un controlador que no
           coincide con el path indicado en la petición.
        
        Este método sólo se debe de invocar si el recurso tiene asociado un
        controlador.
        """
        match = self.base_regexp.match(request.path_info)
        if match is None:
            return http.HttpResponseNotFound()
        
        params = match.groupdict()
        extra = { 'nested_url': params.pop('extra_controller') }

        response = self.controller.dispatch(request, params, **extra)

        if isinstance(response, http.response.HttpResponse):
            return response
            
        response_data = response

        accepts = sorted(
            [
                [key, request.accept[key]]
                for key in request.accept.keys()
            ],
            key=lambda accept: accept[1],
            reverse=True
        )

        any_accepted = None
        for accept in accepts:
            accept_subtype = accept[0].split("/")[1]
            if accept_subtype in self.renders:
                try:
                    resource_params = self.renders[accept_subtype].get_params(
                        self,
                        accept,
                        accept_subtype,
                    )

                    any_accepted = True
                    break

                except RenderParamsException as exception:
                    pass
        
        if not any_accepted:
            raise http.HttpResponseUnsupportedMediaType()
        
        # Execute the necessary context_processors
        context_data = {}
        for context_processor in self.context_processors:
            context_data.update(
                context_processor(
                    request,
                    params
                )
            )
        
        # Render the template with response + request + contexts_info
        context_data.update(response_data)
        
        response = http.HttpResponseOk(
            content = self.renders[accept_subtype].render(
                context_data,
                **resource_params
            ),
            content_type = accept[0]
        )
        
        return response
