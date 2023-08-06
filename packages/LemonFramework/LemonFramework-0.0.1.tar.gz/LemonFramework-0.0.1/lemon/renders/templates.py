"""
This file is part of Lemon.

Lemon is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lemon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lemon.  If not, see <http://www.gnu.org/licenses/>.


Copyright (c) 2012 Vicente Ruiz <vruiz2.0@gmail.com>
"""
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from lemon.core.utils.decorators import cached_property
from lemon.renders.base import Render
from lemon.renders.exceptions import RenderParamsException


class Jinja2Render(Render):
    @cached_property
    def env(self):
        """
        Prepara el entorno en función de la configuración. Una vez construido el
        entorno se cachea para su posterior uso.
        """
        from lemon.core.config import LemonConfig
        config = LemonConfig()
        template_path = config.templates['directory']

        # TODO @1
        # Esto se debería cargar desde settings y dar lugar a varios entornos
        # de búsqueda, como distintos directorios
        env = Environment(loader=FileSystemLoader(template_path))

        return env

    def get_params(self, resource, accept_type, accept_subtype):
        """Ver ``Render.get_params``"""
        name = resource.name.replace(':', '_')
        template_name = name + "." + accept_subtype
        
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound as exception:
            raise RenderParamsException('Template not found')

        return {
            'template': template,
        }

    def render(self, context_data, **params):
        # TODO @1
        # Si falla la carga de la plantilla, mirar automáticamente en el
        # siguiente entorno
        #template = self.env.loader.load(self.env, params['template_name'])
        template = params['template']
        return template.render(context_data)
