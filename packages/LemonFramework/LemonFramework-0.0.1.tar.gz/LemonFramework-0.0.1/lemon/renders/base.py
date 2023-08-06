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
import abc


class Render(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def render(self, *args, **kwargs):
        pass

    def get_params(self, resource, accept_type, accept_subtype):
        """
        Prepara los parámetros que se necesitan para utilizar en el método
        ``render``. Por lo general, no son necesarios parámetros, pero en
        aquellos que necesitan generar un nombre de plantilla, se puede hacer
        a través de éste método.

        ``resource`` Recurso que va a renderizar. Ej: 'index'
        ``accept_type`` Accept Type del request que se está evaluando. Ej: 'text/html'
        ``accept_subtype`` Subtipo de Accept Type del request que se está evaluando. Ej: 'html'

        Puede lanzar ``RenderParamsException``, para indicar que no hubo éxito
        en la obtención de los parámetros.
        """
        return {}



