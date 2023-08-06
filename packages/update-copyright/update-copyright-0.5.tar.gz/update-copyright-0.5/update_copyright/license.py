# Copyright (C) 2009-2013 W. Trevor King <wking@tremily.us>
#
# This file is part of update-copyright.
#
# update-copyright is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# update-copyright is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# update-copyright.  If not, see <http://www.gnu.org/licenses/>.

import textwrap as _textwrap


LICENSE = """
Copyright (C) 2009-2013 W. Trevor King <wking@tremily.us>

This file is part of update-copyright.

update-copyright is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

update-copyright is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
update-copyright.  If not, see <http://www.gnu.org/licenses/>.
""".strip()

def short_license(info, wrap=True, **kwargs):
    paragraphs = [
        'Copyright (C) 2009-2013 W. Trevor King <wking@tremily.us>'.format(**info),
        'update-copyright comes with ABSOLUTELY NO WARRANTY and is licensed under the GNU General Public License.'.format(**info),
        ]
    if wrap:
        for i,p in enumerate(paragraphs):
            paragraphs[i] = _textwrap.fill(p, **kwargs)
    return '\n\n'.join(paragraphs)
