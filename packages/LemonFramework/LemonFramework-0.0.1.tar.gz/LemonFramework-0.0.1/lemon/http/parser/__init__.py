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
from lemon.http.exceptions import HttpAcceptHeaderParserException
from lemon.http.parser import expressions


def parse_accept_header(accept_header):
    if not expressions.ACCEPT.match(accept_header):
        raise HttpAcceptHeaderParserException("ACCEPT HEADER is not valid")

    media_range = {}
    for it in expressions.ACCEPT_MEDIA_RANGE.finditer(accept_header):
        media_type = it.group('type') or '*'
        media_subtype = it.group('subtype') or '*'
        media_q = float(it.group('q') or 1.0)

        key = '%s/%s' % (media_type, media_subtype)
        # Check if media type is in ``media_range``. In this case, get
        # the highest value for ``media_q``
        if key in media_range:
            prev_q = media_range[key]
            if prev_q > media_q:
                media_q = prev_q
        # Store the quality for this media type
        media_range[key] = media_q

    return media_range
