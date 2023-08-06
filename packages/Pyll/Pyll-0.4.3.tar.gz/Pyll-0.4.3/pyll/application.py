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
from webob import Request, Response
from json import loads, dumps
from webob import exc
from webob.exc import status_map

import inspect
import sys
import logging
import pyll
from pyll import config, auth_id, permissions
from paste.debug.profile import profile_decorator
from paste.recursive import ForwardRequestException
from paste.recursive import RecursiveMiddleware
from paste.errordocument import StatusKeeper

log = logging.getLogger(__name__)

class PyllContext(object):
    '''This is the class that holds all the context variables per request.
    (thead local)

    Do what you want with it, but I probably would leave it as storage only ;)
    '''
    pass

class WSGIApp(object):
    '''This is the base class from where all controllers are derived.  It sets
    up the request enviroment and registers them to pastes registry, for thread
    local access per request.
    '''

    #    @profile_decorator(logfile='stdout')
    #    def __begin__(self):
    #        pass

    def __init__(self):
        self.config = config or pyll.config._current_obj()
        package_name = config['pyll.package']
        self.helpers = config['pyll.h']
        self.globals = config.get('pyll.app_globals')
        self.environ_config = config['pyll.environ_config']
        self.package_name = package_name
        self.log_debug = False
        self.config.setdefault('lang', 'en')
        self.auth_id = None
        self.permissions = None

        # Cache some options for use during requests
        self._session_key = self.environ_config.get('session', 'beaker.session')
        self._cache_key = self.environ_config.get('cache', 'beaker.cache')

    def _register(self, environ):
        # do the paste registry
        obj = environ['pyll.pyll']

        registry = environ['paste.registry']
        registry.register(pyll.response, obj.response)
        registry.register(pyll.request, obj.request)
        registry.register(pyll.app_globals, self.globals)
        registry.register(pyll.config, self.config)
        registry.register(pyll.auth_id, self.auth_id)
        registry.register(pyll.permissions, self.permissions)
        registry.register(pyll.tmpl_context, obj.tmpl_context)

        if 'session' in obj.__dict__:
            registry.register(pyll.session, obj.session)
        if 'cache' in obj.__dict__:
            registry.register(pyll.cache, obj.cache)
        elif 'cache' in obj.app_globals.__dict__:
            registry.register(pyll.cache, obj.app_globals.cache)

    def _setup_registery(self, environ, start_response):
        # Setup the basic pyll thread-local objects
        req = Request(environ)
        req.config = self.config
        response = Response()

        # Store a copy of the request/response in environ for faster access
        obj = PyllContext()
        obj.config = self.config
        obj.request = req
        obj.response = response
        obj.app_globals = self.globals
        obj.auth_id = self.auth_id
        obj.permissions = self.permissions
        obj.h = self.helpers

        environ['pyll.pyll'] = obj
        environ['pyll.environ_config'] = self.environ_config

        tmpl_context = PyllContext()
        obj.tmpl_context = req.tmpl_context = tmpl_context

        if self._session_key in environ:
            obj.session = req.session = environ[self._session_key]
        if self._cache_key in environ:
            obj.cache = environ[self._cache_key]

        # Load the globals with the registry if around
        if 'paste.registry' in environ:
            self._register(environ)

    # verify utility for dispatching to controller methods
    def _has_method(self, action):
        v = vars(self.__class__)
        return action in v and inspect.isroutine(v[action])

    def __call__(self, environ, start_response, action, vars):
        '''A requirement of the controller object, is that it is callable.
        Most of the routing is done in the RouteFactory.
        '''
        resp = None

        if 'REMOTE_USER' in environ:
            self.auth_id = environ['AUTH_ID']
            self.permissions = environ['PERMISSIONS']
        else: # we have deleted the REMOTE_USER so delete the other keys
            if 'AUTH_ID' in environ:
                del environ['AUTH_ID']
                self.auth_id = None
            if 'PERMISSIONS' in environ:
                del environ['PERMISSIONS']
                self.permissions = None

        # setup req
        self.request = Request(environ)

        # set session from cache
        self.request.session = environ[self._session_key]

        # Local this thread and register variables for this request.
        self._setup_registery(environ, start_response)

        try:
            if self._has_method(action):
                # Get the method from the derived class
                resp = getattr(self, action)(**vars)
            else:
                raise exc.HTTPNotFound("Method not found for controller: %s"
                                       % self.__class__.__name__)

            if isinstance(resp, dict):
                # Deprecated mostly...
                if 'redirect_login' in resp:
                    log.debug("No auth header, so redirecting...")
                    raise ForwardRequestException(self.globals.login_path)

            # See if it is just a string output
            if isinstance(resp, basestring):
                log.debug("String body response...")
                # assign it to the response body
                resp = Response(body=resp)

            if resp is None:
                resp = Response(body="Failed!")

            return resp(environ, start_response)

        except AttributeError, e:
            resp = Response(body="Failed: %s" % e)

        except RuntimeError, e:
            resp = Response(body="Failed: %s" % e)

        except exc.HTTPException, e:
            # The exception object itself is a WSGI application/response:
            print "Excepted: %s" % e
            resp = e

        return resp(environ, start_response)
