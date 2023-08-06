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


class Handler(metaclass=AspectType):
    def __init__(self):
        # Load the current configuration
        from lemon.core.config import LemonConfig
        self.config = LemonConfig()
    
    def dispatch(self, request):
        """Dada una petición HTTP, este método se encarga de generar la
        respuesta HTTP adecuada. Para ello, primero se hace un matching con la
        URL, se ubica el recurso adecuado y se le solicita que atienda la
        petición."""
        # Matching
        match = None
        for resource in self.config.urls:
            match = resource.match(request.path_info)
            if match is not None:
                break
        
        # Se comprueba si se ha encontrado la URL solicitada
        if match is None:
            raise http.HttpResponseNotFound()
        # Se atiende la petición por el recurso adecuado
        return resource.attend(request)
