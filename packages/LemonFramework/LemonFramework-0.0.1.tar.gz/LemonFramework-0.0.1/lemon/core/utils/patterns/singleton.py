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
class SingletonType(type):
    def __init__(cls, name, bases, classdict):
        super().__init__(name, bases, classdict)
        cls._singleton_instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._singleton_instance is None:
            try:
                cls._singleton_instance = super().__call__(*args, **kwargs)
            except Exception as exception:
                cls._singleton_instance = None
                raise exception
        
        return cls._singleton_instance


class Singleton(metaclass=SingletonType):
    @classmethod
    def invalidateInstance(cls):
        cls._singleton_instance = None
    
    @classmethod
    def getInstance(cls):
        if cls._singleton_instance is None:
            cls()
        return cls._singleton_instance
