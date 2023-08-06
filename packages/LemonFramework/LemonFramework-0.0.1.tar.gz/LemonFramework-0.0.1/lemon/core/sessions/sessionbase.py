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
import uuid


class SessionBase(metaclass=abc.ABCMeta):
    """
    This class represent a Session on server-side. A subclass must have
    like-dict behavior.
    """
    @abc.abstractmethod
    def __init__(self, cookie, sid):
        pass

    @abc.abstractmethod
    def get_cookie(self):
        """Must return a http.cookies.SimpleCookie object"""
        pass

    @abc.abstractmethod
    def save(self):
        pass

    def get_identifier(self):
        return str(uuid.uuid1())
