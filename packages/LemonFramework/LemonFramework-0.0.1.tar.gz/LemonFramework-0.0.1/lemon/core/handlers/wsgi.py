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
from lemon.http.exceptions import HttpParserException, HttpResponseException
from lemon.core.exceptions import LemonException
from lemon.core.handlers.handlerbase import Handler


class WSGIHandler(Handler):
    def __call__(self, environ, start_response):
        try:
            request = http.HttpRequest(environ)
            response = self.dispatch(request)
        except (UnicodeDecodeError, HttpParserException) as exception:
            response = http.HttpResponseBadRequest()
        except HttpResponseException as exception:
            response = exception
        except LemonException as exception:
            response = http.HttpResponseInternalServerError()
        #except:
        #    response = http.HttpResponseInternalServerError()

        start_response(response.status, response.headers)
        return response.content
