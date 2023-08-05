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
import os
import time
import logging

from webob import exc
from webob.exc import status_map
from webob import Response

import functools
from functools import wraps
import inspect

from genshi.core import Stream
from genshi.output import encode, get_serializer
from genshi.template import Context, TemplateLoader

from pyll import tmpl_context as c, session, config
import pyll
from paste.recursive import ForwardRequestException
from paste.recursive import RecursiveMiddleware
from paste.errordocument import StatusKeeper

from json import dumps, loads
from decorator import decorator

from jinja2 import Environment, PackageLoader
jinja_env = Environment(loader=PackageLoader(config['pyll.package'], 'templates/html'))

log = logging.getLogger(__name__)

# Loader used for Genshi
loader = TemplateLoader(
    os.path.join(config['pyll.paths']['root'], 'templates'),
    auto_reload=True
)

# Forward via recursion middleware exception handling.
def forward(url, code=301):
    raise ForwardRequestException(url)

# Redirect for urls.
def redirect(url, code=302):
    raise exc.HTTPTemporaryRedirect(location=url)

class AuthenticationError(Exception):
    message="Authentication error or incorrect permissions."

    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)

# Simple auth checking
class Authenticated(object):
    def fn(self):
        if 'user' in session:
            return True
        else:
            return False

authenticated = Authenticated()

# Credential class for getting current credential entitlements from the user
# session.  When you write your login/auth handler, you will need to make sure
# the user object is a picklable user object with __repr__ returning anything
# you want actually stored in the session. Pay close attention to the
# user.permissions ;)
class Credential(object):
    error_msg = u'Needs to have at least this permission.'

    def __init__(self, credentials_needed):
        self.credentials_needed = str(credentials_needed).split()

    def fn(self):
        req = pyll.request._current_obj()
        if 'REMOTE_USER' in req.environ:
            try:
                permissions = str(req.environ['PERMISSIONS']).strip("[]").split(",")
                if permissions:
                    for permission in permissions:
                        for credential in self.credentials_needed:
                            if str(credential) == str(permission):
                                return True
                    return False
                else:
                    return False
            except Exception, e:
                log.debug("Excepted in credential: %s" % e)
                return False
        else:
            return False

credential = Credential

# @authorize decorator that takes credential arguments in a space or comma
# separated list e.g. credential('admin droid') etc.
def authorize(valid):
    def validate(func, self, *args, **kwargs):
        try:
            if valid.fn():
                return func(self, *args, **kwargs)
            else:
                log.debug("User permissions or not logged in...")
                g = pyll.app_globals._current_obj()
                return forward(g.login_path, 301)
        except AuthenticationError, e:
            return AuthenticationError(e)
    return decorator(validate)

# Decorator for Genshi rendering.  This sets up the template object for
# later use in rendering output.
def xml(filename, method='html', encoding='utf-8', **options):
    """Decorator for exposed methods to specify what template they should use
    for rendering, and which serialization method and options should be
    applied.
    """
    xmldir = 'xml/'

    def decorate(func):
        def wrapper(*args, **kwargs):
            c = pyll.tmpl_context._current_obj()
            c.template = loader.load(xmldir+filename)
            opt = options.copy()
            if method == 'html':
                opt.setdefault('doctype', 'html')
            serializer = get_serializer(method, **opt)
            stream = func(*args, **kwargs)
            if not isinstance(stream, Stream):
                return stream
            return encode(serializer(stream), method=serializer,
                encoding=encoding)
        return wrapper
    return decorate

# Genshi rendering for the decorator above.
def xml_render(*args, **kwargs):
    """Function to render the given data to the template specified via the
    ``@xml`` decorator.
    """
    globals = {}
    c = pyll.tmpl_context._current_obj()
    g = pyll.app_globals._current_obj()
    session = pyll.session._current_obj()

    if args:
        assert len(args) == 1,\
        'Expected exactly one argument, but got %r' % (args,)
        template = loader.load(args[0])
    else:
        template = c.template
    ctxt = Context()
    ctxt.push(kwargs)
    globals.update(kwargs)
    return template.generate(g=g, globals=globals, c=c, session=session)

# Jinjna2 Template decorator.  Here is where you could do something custom,
# or add your own favorite template engine.
# I just happen to really dig jinja2 ;)
def html(filename):
    def decorate(func):
        def wrapper(*args, **kwargs):
            c = pyll.tmpl_context._current_obj()
            c.template = jinja_env.get_template(filename)
            return func(*args, **kwargs)
        return wrapper
    return decorate

# Rendering for above...
def html_render(*args, **kwargs):
    globals = {}
    g = pyll.app_globals._current_obj()
    session = pyll.session._current_obj()
    c = pyll.tmpl_context._current_obj()
    #globals.update(c=c)

    if args:
        assert len(args) == 1,\
        'Expected exactly one argument, but got %r' % (args,)
        template = jinja_env.get_template(args[0])
    else:
        template = c.template
    globals.update(kwargs)
    return template.render(session=session, globals=globals, g=g, c=c)

# JSON decorator.. and yes, this was painful (supports args, parenthesis, or
# not).  Remember to add the auth decorators if you want your API protected. I
# had thought about consolidating, but after looking at the syntax, this way
# is actually less keystrokes %^)
def jsonify(func):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            string = fn(*args, **kwargs)
            def json_response(string):
                res = Response(content_type='application/json')
                res.body = dumps(string)
                return res
            return json_response(string)
        return wrapper
    if inspect.isfunction(func):
        return decorator(func)
    else:
        return decorator

