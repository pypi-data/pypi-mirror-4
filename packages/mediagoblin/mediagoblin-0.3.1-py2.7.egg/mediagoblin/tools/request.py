# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from mediagoblin.db.util import ObjectId, InvalidId

_log = logging.getLogger(__name__)


def setup_user_in_request(request):
    """
    Examine a request and tack on a request.user parameter if that's
    appropriate.
    """
    if not request.session.has_key('user_id'):
        request.user = None
        return

    try:
        oid = ObjectId(request.session['user_id'])
    except InvalidId:
        user = None
    else:
        user = request.db.User.find_one({'_id': oid})

    if not user:
        # Something's wrong... this user doesn't exist?  Invalidate
        # this session.
        _log.warn("Killing session for user id %r", request.session['user_id'])
        request.session.invalidate()

    request.user = user
