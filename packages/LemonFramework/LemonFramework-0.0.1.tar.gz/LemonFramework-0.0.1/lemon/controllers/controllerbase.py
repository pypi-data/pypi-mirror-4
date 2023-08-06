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
from lemon import http
from lemon.core.aspects import AspectType
from lemon.core.utils.decorators import cached_property


class Controller(metaclass=AspectType):
    
    @cached_property
    def permitted_methods(self):
        methods = tuple([
            method_name
            for method_name in http.HTTP_METHODS
            if getattr(self, method_name.lower(), None)
        ])
        
        return methods

    def dispatch(self, request, params, **kwargs):
        method_name = request.method.lower()
        
        try:
            method = getattr(self, method_name)
        except AttributeError:
            raise http.HttpResponseMethodNotAllowed(self.permitted_methods)
        
        return method(request, params)

    def get_urls(self):
        """
        Genera una lista con todas las urls anidadas dentro de este controlador.
        Debe de devolver un listado de tuplas (url, name).
        """
        return ()
