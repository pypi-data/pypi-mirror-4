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
from http.cookies import SimpleCookie

from lemon.aspects import Aspect
from lemon.core.sessions.exceptions import InvalidSessionSettingsException
from lemon.core.utils.decorators import cached_property


from lemon.core.sessions.filesystem import FileSystemSession

__all__ = ['SessionAspect', 'FileSystemSession']


class SessionAspect(Aspect):
    @cached_property
    def settings(self):
        from lemon.core.config import LemonConfig
        config = LemonConfig()
        return config.settings
        
    @cached_property
    def expires(self):
        session_settings = self.settings.get('sessions')
        if session_settings is not None:
            # Getting the expires function
            expires_func = None
            expires = self.settings.get('expires', '')
            if expires:
                if isinstance(expires, str):
                    try:
                        expires = import_object(expires)
                    except ImportError as error:
                        raise InvalidSessionSettingsException(error)

                if callable(expires):
                    expires_func = expires
                else:
                    raise InvalidSessionSettingsException(
                        "'expires' setting is not callable"
                    )

            return expires_func or expires
        return ''

    @cached_property
    def path(self):
        session_settings = self.settings.get('sessions')
        if session_settings is not None:
            return self.settings.get('path', '') or ''
        return ''

    @cached_property
    def comment(self):
        session_settings = self.settings.get('sessions')
        if session_settings is not None:
            return self.settings.get('comment', '') or ''
        return ''

    @cached_property
    def domain(self):
        session_settings = self.settings.get('sessions')
        if session_settings is not None:
            return self.settings.get('domain', '') or ''
        return ''

    @cached_property
    def max_age(self):
        session_settings = self.settings.get('sessions')
        if session_settings is not None:
            return self.settings.get('max_age', '') or ''
        return ''

    @cached_property
    def secure(self):
        session_settings = self.settings.get('sessions')
        if session_settings is not None:
            return self.settings.get('secure', '') or ''
        return ''

    @cached_property
    def version(self):
        session_settings = self.settings.get('sessions')
        if session_settings is not None:
            return self.settings.get('version', '') or ''
        return ''

    @cached_property
    def httponly(self):
        session_settings = self.settings.get('sessions')
        if session_settings is not None:
            return self.settings.get('httponly', '') or ''
        return ''

    def around(self, resource_obj, request, *args, **kwargs):
        # Retrive the session cookie
        sid = request.cookies.get('sid')
        if sid: # Retrieve a previous session
            #session_cookie = SimpleCookie() # Just 'sid' cookie
            #session_cookie['sid'] = request.cookies['sid'].value
            #session_cookie['sid'].update(request.cookies['sid'])
            #session = Session(request.cookies, request.cookies['sid'].value)
            sid = request.cookies['sid'].value
            session_cookie = request.cookies
        else: # New session
            sid = None
            session_cookie = SimpleCookie()
            session_cookie['sid'] = ''
            if self.expires:
                session_cookie['sid']['expires'] = self.expires()
            session_cookie['sid']['path'] = self.path
            session_cookie['sid']['comment'] = self.comment
            session_cookie['sid']['domain'] = self.domain
            session_cookie['sid']['max-age'] = self.max_age
            session_cookie['sid']['secure'] = self.secure
            session_cookie['sid']['version'] = self.version
            session_cookie['sid']['httponly'] = self.httponly
            #session = Session(session_cookie)

        Session = self.settings['sessions']['class']
        session = Session(session_cookie, sid)
        # Link the session to request
        request.session = session
        
        response = self.execute(resource_obj, request, *args, **kwargs)
        
        # Check if it is a new session
        sid = request.cookies.get('sid')
        if not sid:
            response.set_cookies(session.get_cookie())
        # Save the changes on server
        session.save()
        
        return response

