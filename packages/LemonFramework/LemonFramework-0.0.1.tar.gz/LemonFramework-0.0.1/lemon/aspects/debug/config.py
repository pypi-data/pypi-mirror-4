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
import logging

from lemon.aspects.logging import LoggingAspect


class DebugConfigAspect(LoggingAspect):
    def __init__(self, fn):
        super().__init__(fn, 'lemon.debug')
        
    def after(self, handler_obj, *args, **kwargs):
        print('DebugConfigAspect')
        for resource in handler_obj.config.urls:
            print('URL:', resource)
        #self.logger.info('Before of function: %s, Args: %s, KWArgs: %s' % (
                #self.function.__name__,
                #args,
                #kwargs,
            #)
        #)
    
    def before(self, *args, **kwargs):
        """Override ``LoggingAspect`` behaviour."""
    
    def exception(self, exception, *args, **kwargs):
        """Override ``LoggingAspect`` behaviour."""
