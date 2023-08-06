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
from lemon.core.config.urls import load_urls
from lemon.core.utils.imports import import_object


class ConfigType(type):
    """Se utiliza como metaclase para las clases de configuración. Implementa
    el patrón de diseño Singleton."""
    def __new__(mcs, name, bases, classdict):
        config_attrs = {}
        
        # Recuperamos todos los atributos de clase de cada una de las clases
        # bases y los almacenamos en ``config_attrs``
        for base in bases:
            # Lo primero es recpuerar las opciones almacenadas en la clase base.
            if '_config_options' in base.__dict__:
                config_attrs.update(base.__dict__['_config_options'])
            # Recuperamos los atributos.
            for key, value in base.__dict__.items():
                if not key.startswith('_'):
                    config_attrs[key] = value
        
        # Utilizamos ``new_classdict`` para almacenar todos los atributos
        # privados de la clase (los que empiezan por _) y el resto los añadimos
        # a ``config_attrs`` para conseguir la lista completa de opciones de
        # configuración.
        new_classdict = {}
        for key, value in classdict.items():
            if not key.startswith('_'):
                config_attrs[key] = value
            else:
                new_classdict[key] = value
        
        # Añadimos el atributo ``_config_options`` como atributo privado para la
        # creación de la clase. Este atributo se parseará a la hora de recuperar
        # la instancia.
        new_classdict['_config_options'] = config_attrs
        # Devolvemos el nuevo tipo, con los atributos almacenados en el
        # atributo ``new_classdict``.
        return type.__new__(mcs, name, bases, new_classdict)
    
    def __init__(cls, name, bases, classdict):
        super().__init__(name, bases, classdict)
        cls._config_instance = None
    
    def __call__(self, *args, **kwargs):
        if self._config_instance is None:
            config_instance = super().__call__(*args, **kwargs)
            
            # Preparamos los atributos de la instancia
            config_instance.aspects = self.config_aspects(
                self._config_options['aspects']
            )
            config_instance.debug = self._config_options['debug']
            
            self.config_logging(self._config_options['logging'])
            config_instance.settings = self.config_settings(
                self._config_options['settings']
            )
            config_instance.urls = self.config_urls(
                self._config_options['urls']
            )
            
            # TODO: Hay que cambiar los settings de plantillas, renders, ....
            config_instance.templates = self._config_options.get('templates', {})
            # TODO: Hay que cambiar los settings de media y static ....
            config_instance.media = self._config_options.get('media', {})
            config_instance.static = self._config_options.get('static', {})
            
            # TODO: Esto implementarlo como un aspecto
            #for resource in config_instance.urls:
            #    print('URL:', resource)
            
            self._config_instance = config_instance
        
        return self._config_instance
    
    def config_aspects(self, aspects_config):
        from lemon.core.handlers.handlerbase import Handler
        from lemon.core.config.urls.resource import Resource
        
        for aspect_type, aspect_list in aspects_config.items():
            imported_aspect_list = []
            # Preparamos la lista de aspectos (se aplican en orden inverso)
            aspect_list = list(aspect_list)
            aspect_list.reverse()
            for aspect in aspect_list:
                if isinstance(aspect, str):
                    aspect = import_object(aspect)
                imported_aspect_list.append(aspect)
            
            aspects_config[aspect_type] = tuple(imported_aspect_list)
        # Se aplican los aspectos a las distintas partes del framework
        for aspect in aspects_config['application']:
            Handler.pointcut('__call__', aspect)
        
        for aspect in aspects_config['flow']:
            Handler.pointcut('dispatch', aspect)
        
        for aspect in aspects_config['session']:
            Resource.pointcut('attend', aspect)
                
        return aspects_config
    
    def config_logging(self, log_config):
        from logging.config import dictConfig
        dictConfig(log_config)
    
    def config_settings(self, settings_config):
        # TODO @1: Estos chequeos se deberían hacer en la propia clase Aspect
        if 'sessions' in settings_config:
            if not 'class' in settings_config['sessions']:
                from lemon.core.sessions.exceptions import InvalidSessionSettingsException
                raise InvalidSessionSettingsException(
                        "'class' setting is not defined"
                    )
            session_class = settings_config['sessions']['class']
            if isinstance(session_class, str):
                settings_config['sessions']['class'] = import_object(session_class)
        return settings_config
    
    def config_urls(self, urls_config):
        urls = load_urls(urls_config)
        # TODO: Recorrer todas las urls generadas para ver si se repiten exp.reg.
        # y mostrar un aviso de conflicto
        # TODO: Localizar urls inaccesibles y mostrar un aviso
        return urls
