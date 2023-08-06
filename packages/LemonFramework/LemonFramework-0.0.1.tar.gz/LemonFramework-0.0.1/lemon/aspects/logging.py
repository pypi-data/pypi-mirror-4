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

from lemon.aspects import Aspect


class LoggingAspect(Aspect):
    def __init__(self, fn, logger):
        super().__init__(fn)
        self.logger = logging.getLogger(logger)
        
    def before(self, *args, **kwargs):
        self.logger.info('Before of function: %s, Args: %s, KWArgs: %s' % (
                self.function.__name__,
                args,
                kwargs,
            )
        )
    
    def after(self, *args, **kwargs):
        self.logger.info('After of function: %s, Args: %s, KWArgs: %s' % (
                self.function.__name__,
                args,
                kwargs,
            )
        )
    
    def exception(self, exception, *args, **kwargs):
        self.logger.info('Exception: %s during the execution of function: %s' % (
                exception,
                self.function.__name__,
            )
        )
        # Relanzamos la excepción
        raise exception
