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

from routes.route import Route

auth_routes = [
    Route('mediagoblin.auth.register', '/register/',
          controller='mediagoblin.auth.views:register'),
    Route('mediagoblin.auth.login', '/login/',
          controller='mediagoblin.auth.views:login'),
    Route('mediagoblin.auth.logout', '/logout/',
          controller='mediagoblin.auth.views:logout'),
    Route('mediagoblin.auth.verify_email', '/verify_email/',
          controller='mediagoblin.auth.views:verify_email'),
    Route('mediagoblin.auth.resend_verification', '/resend_verification/',
          controller='mediagoblin.auth.views:resend_activation'),
    Route('mediagoblin.auth.resend_verification_success',
          '/resend_verification_success/',
          template='mediagoblin/auth/resent_verification_email.html',
          controller='mediagoblin.views:simple_template_render'),
    Route('mediagoblin.auth.forgot_password', '/forgot_password/',
          controller='mediagoblin.auth.views:forgot_password'),
    Route('mediagoblin.auth.verify_forgot_password',
          '/forgot_password/verify/',
          controller='mediagoblin.auth.views:verify_forgot_password')]
