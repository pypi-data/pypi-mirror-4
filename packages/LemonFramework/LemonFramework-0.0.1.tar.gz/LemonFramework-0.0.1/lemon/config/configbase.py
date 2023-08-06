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
from lemon.core.config import ConfigType


class ConfigBase(metaclass=ConfigType):
    aspects = {
        'application': (),
        'flow': (),
        'session': (),
    }
    
    debug = False
    
    logging = {
        'version': 1,

        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'default': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s [%(levelname)-5s] [%(name)s] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },

        'handlers': {
            'default': {
                'level': 'INFO',
                'class': 'logging.NullHandler',
                'formatter': 'default',
            },
            'console':{
                'level':'DEBUG',
                'class':'logging.StreamHandler',
                'formatter': 'simple'
            },
        },

        'loggers': {
            'lemon': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True,
            },
            'lemon.config': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True,
            },
            'lemon.request': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True,
            },
            'lemon.debug': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
    
    persistence = {}
    settings = {}
    urls = {}
    
    media = {
        'url': '/media/',
        'root': 'public/media',
    }
    
    static = {
        'url': '/static/',
        'root': 'public/static',
    }
    
    templates = {
        'directory': 'templates',
    }
