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
import mimetypes
import os

from lemon import http
from lemon.aspects import Aspect
from lemon.http import HttpResponseNotFound, HttpResponseOk
from lemon.core.utils.decorators import cached_property


class ServingFilesAspect(Aspect):
    @cached_property
    def paths(self):
        from lemon.core.config import LemonConfig
        config = LemonConfig()
        path_info = {}
        # Media files
        media_url = config.media.get('url', None)
        media_root = config.media.get('root', None)
        if media_url and media_root:
            path_info.update({ media_url: media_root })
        # Static files
        static_url = config.static.get('url', None)
        static_root = config.static.get('root', None)
        if static_url and static_root:
            path_info.update({ static_url: static_root })

        return path_info

    def get_file(self, path):
        mimetype, encoding = mimetypes.guess_type(path)
        mimetype = mimetype or 'application/octet-stream'

        with open(path, 'rb') as f:
            name = f.name
            data = f.read()

        return {
            'mimetype': mimetype,
            'encoding': encoding,
            'filename': name,
            'content': data,
        }
    
    def exception(self, exception, handler_obj, request, *args, **kwargs):
        for url, base_path in self.paths.items():
            if request.path_info.startswith(url):
                resource = request.path_info.replace(url, '', 1)
                file_path = os.path.join(base_path, resource)
                if os.path.isfile(file_path):
                    response = http.HttpResponseOk()

                    data = self.get_file(file_path)
                    response.set_content(
                        data['content'],
                        data['mimetype'],
                        data['encoding'],
                    )

                    return response
        # Si no se trata de un fichero que se va a servir, relanzamos la
        # excepción
        raise exception


