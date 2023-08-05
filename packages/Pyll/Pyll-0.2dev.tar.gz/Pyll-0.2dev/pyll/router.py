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
import sys
import re
import pyll
from webob import Request, Response
from webob import exc
from json import loads, dumps


# Map container object for regex templates, actions, and variable storage.
class Map():
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


class RouteFactory(object):
    '''This is the handler dispatching mechanism for the controllers/method
    matching, and request routing.


    init takes a list of Map objects and compiles regexes to match URI
    requests. Upon a matching request, dispatch looks up the module, imports
    it, calls the callable class derived from ControllerBase and dispatches the
    request to the reponse object, or returns 404.

    If you want to do more than two layers of variable matching for your API,
    or ReST engine, You may wish to add more regular expression templates for
    your URI to variable parsing.

    Example:
        my other_var_name = match.group(3)
        my_other_expr = match.group(4)

        They will still be available in the req.urlvars.

    '''

    # URI regex template
    uri_regex = re.compile(r'''
         \{          # The exact character "{"
         (\w+)       # The variable name (restricted to a-z, 0-9, _)
         (?::([^}]+))? # The optional :regex part
         \}          # The exact character "}"
         ''', re.VERBOSE)

    def __init__(self, routes):
        self.routes = []

        for route in routes:
            self.add_route(route)

    # Add route to the factory object
    def add_route(self, route):
        self.routes.append((re.compile(self.template_to_regex(route.template)), route))

    # Compile the the regex
    # Mucho Thanks to Ian Bicking for the awesome template examples.
    def template_to_regex(self, template):
        regex = ''
        last_pos = 0
        for match in self.uri_regex.finditer(template):
            regex += re.escape(template[last_pos:match.start()])
            var_name = match.group(1)
            expr = match.group(2) or '[^/]+'
            expr = '(?P<%s>%s)' % (var_name, expr)
            regex += expr
            last_pos = match.end()
        regex += re.escape(template[last_pos:])
        regex = '^%s$' % regex
        return regex

    # Route down to the controller if we match
    def __call__(self, environ, start_response):
        req = Request(environ)

        for regex, route in self.routes:
            match = regex.match(req.path_info)

            if match:
                req.urlvars = match.groupdict()
                req.urlvars.update(route.__dict__)

                if 'action' in req.urlvars: 
                   return self.dispatch(environ, start_response, route.handler, req.urlvars['action'], req.urlvars)
                else:
                    # NOTE: This really should never happen...
                    return self.dispatch(environ, start_response, route.handler, route.action, req.urlvars)

        # Nothing matched so 404 it...
        return exc.HTTPNotFound()(environ, start_response)

    # Dispatch to the controller dynamically...
    def dispatch(self, environ, start_response, handler, action, vars):
        module_name, klass = handler.split(':', 1)
        __import__(module_name)
        module = sys.modules[module_name]
        klass = getattr(module, klass)
        return klass()(environ, start_response, action, vars)
