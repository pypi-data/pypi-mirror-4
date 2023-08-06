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
from lemon.core.exceptions import LemonException


class ConfigException(LemonException): pass


class InvalidConfigException(LemonException):
    """Esta excepción se lanza si ocurre cualquier problema durante la
    configuración del sistema."""

class URLBadFormedException(InvalidConfigException):
    """This exception is launched by ``Resource`` when it try to compile a url
    to regular expresion."""
