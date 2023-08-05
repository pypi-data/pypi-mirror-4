"""
    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is Pyll.

    The Initial Developer of the Original Code is Noel Morgan,
    Copyright (c) 2012 Noel Morgan. All Rights Reserved.

    http://www.pyll.org/

    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations
    of liability) contained within the Source Code Form of the Covered Software,
    except that You may alter any license notices to the extent required to
    remedy known factual inaccuracies.
"""
import pyll
from paste.recursive import ForwardRequestException
from pyll import tmpl_context as c, session, app_globals, auth_id
from webob import Request, Response
from webob import exc


def auth_user_id():
    try:
        auth_id = pyll.auth_id._current_obj()
        return auth_id
    except TypeError:
        return None

def save_auth(req, user):
    req.environ["REMOTE_USER"] = str(user.username)
    req.environ["AUTH_ID"] = str(user.id)
    req.environ['PERMISSIONS'] = user.permissions
    req.environ["paste.auth.cookie"].append('AUTH_ID')
    req.environ["paste.auth.cookie"].append('PERMISSIONS')

    return req

def remove_auth(req, session):

    if 'REMOTE_USER' in req.environ:
        del req.environ["AUTH_ID"]
        del req.environ["REMOTE_USER"]
        del req.environ['PERMISSIONS']

    g = pyll.app_globals._current_obj()

    if 'user' in session:
        del session['user']
    session.invalidate()
    session.delete()

    raise ForwardRequestException(g.login_path)
