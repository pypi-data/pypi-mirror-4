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
import base64

from pkg_resources import resource_filename

from mediagoblin import mg_globals
from mediagoblin.tools import template, pluginapi
from mediagoblin.tests.tools import get_app, fixture_add_user


_log = logging.getLogger(__name__)

def resource(filename):
    '''
    Borrowed from the submission tests
    '''
    return resource_filename('mediagoblin.tests', 'test_submission/' + filename)


GOOD_JPG = resource('good.jpg')
GOOD_PNG = resource('good.png')
EVIL_FILE = resource('evil')
EVIL_JPG = resource('evil.jpg')
EVIL_PNG = resource('evil.png')
BIG_BLUE = resource('bigblue.png')


class TestAPI(object):
    def setUp(self):
        self.app = get_app(dump_old_app=False)
        self.db = mg_globals.database

        self.user_password = u'4cc355_70k3N'
        self.user = fixture_add_user(u'joapi', self.user_password)

    def login(self):
        self.app.post(
            '/auth/login/', {
                'username': self.user.username,
                'password': self.user_password})

    def get_context(self, template_name):
        return template.TEMPLATE_TEST_CONTEXT[template_name]

    def http_auth_headers(self):
        return {'Authorization': 'Basic {0}'.format(
                base64.b64encode(':'.join([
                    self.user.username,
                    self.user_password])))}

    def do_post(self, data, **kwargs):
        url = kwargs.pop('url', '/api/submit')
        do_follow = kwargs.pop('do_follow', False)

        if not 'headers' in kwargs.keys():
            kwargs['headers'] = self.http_auth_headers()

        response = self.app.post(url, data, **kwargs)

        if do_follow:
            response.follow()

        return response

    def upload_data(self, filename):
        return {'upload_files': [('file', filename)]}

    def test_1_test_test_view(self):
        self.login()

        response = self.app.get(
            '/api/test',
            headers=self.http_auth_headers())

        assert response.body == \
                '{"username": "joapi", "email": "joapi@example.com"}'

    def test_2_test_submission(self):
        self.login()

        response = self.do_post(
            {'title': 'Great JPG!'},
            **self.upload_data(GOOD_JPG))

        assert response.status_int == 200

        assert self.db.MediaEntry.query.filter_by(title=u'Great JPG!').first()
