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
from lemon.core.config.urls.resource import Resource


__all__ = ['Resource', 'load_urls']


def load_urls(url_params):
    url_base = Resource(**url_params)
    urls = []
    if url_base.is_resource():
        urls.extend(url_base.get_urls())
    urls += _load_nested_urls(url_params, url_base)
    return tuple(urls)


def _load_nested_urls(url_params, url_base):
    unordered_urls = []

    for url, params in url_params.items():
        if url.startswith('/'):
            # TODO: Importar las clases
            nested_base = Resource(url, url_base, **params)
            nested_urls = []

            if nested_base.is_resource():
                nested_urls.extend(nested_base.get_urls())
            nested_urls += _load_nested_urls(params, nested_base)

            unordered_urls.append((nested_base, nested_urls))

    urls = []

    if url_base.priority: # This url has priority attribute
        remaining_urls = {}
        # Iterate over priority urls
        for url_name in url_base.priority:
            # Searching the url
            for base, nested_urls in unordered_urls:
                if base.name == url_name:
                    urls += nested_urls
                else:
                    remaining_urls[base] = nested_urls
        for base, nested_urls in remaining_urls.items():
            urls += nested_urls
    else:
        # No priority, no order
        for base, nested_urls in unordered_urls:
            urls += nested_urls

    return urls
