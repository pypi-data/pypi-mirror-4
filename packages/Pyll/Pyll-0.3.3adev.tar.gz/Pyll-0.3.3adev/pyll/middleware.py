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
import sys
import re
import traceback
import itertools
import types
import random
import cgi
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from beaker.middleware import SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool

from weberror import formatter, collector, reporter
from paste import wsgilib
from paste import request
from paste.util import import_string

from webob import Request, Response
from webob import exc
from webob.exc import HTTPForbidden

from weberror.evalexception import make_eval_exception
from weberror.errormiddleware import ErrorMiddleware
from pyll import tmpl_context as c, session


# Mostly ripped from some django implmentation..
class CSRFMiddleware(object):
    """Middleware that adds protection against Cross Site
    Request Forgeries by adding hidden form fields to POST forms and
    checking requests for the correct value. It expects beaker to be upstream
    to insert the session into the environ dict.
    """

    def __init__(self, app, config):
        self.app = app
        self.unprotected_path = config.get('csrf.unprotected_path')

    def __call__(self, environ, start_response):
        request = Request(environ)
        session = environ['beaker.session']
        csrf_token = session.get('csrf')
        if not csrf_token:
            csrf_token = session['csrf'] = str(random.getrandbits(128))
            session.save()

        if request.method == 'POST':
            if (self.unprotected_path is not None
                and request.path_info.startswith(self.unprotected_path)):
                resp = request.get_response(self.app)
                resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
                resp.set_cookie('csrf', csrf_token, max_age=3600)
                return resp(environ, start_response)

            # check for incoming csrf token
            try:
                request_csrf_token = environ.get('HTTP_X_CSRF', request.POST.get('csrftoken'))
                if request_csrf_token != csrf_token:
                    resp = HTTPForbidden("CSRF - Aborted.")
                else:
                    resp = request.get_response(self.app)
            except KeyError:
                resp = HTTPForbidden(_ERROR_MSG)
        else:
            resp = request.get_response(self.app)

        if resp.status_int != 200:
            return resp(environ, start_response)

        resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
        resp.set_cookie('csrf', csrf_token, max_age=3600)

        if resp.content_type.split(';')[0] in ['text/html', 'application/xhtml+xml']:
            # ensure we don't add the 'id' attribute twice (HTML validity)
            idattributes = itertools.chain(('id="csrfmiddlewaretoken"',),
                itertools.repeat(''))
            def add_csrf_field(match):
                """Returns the matched <form> tag plus the added <input> element"""
                return match.group() + '<div style="display:none;">' +\
                       '<input type="hidden" ' + idattributes.next() +\
                       ' name="csrftoken" value="' + csrf_token +\
                       '" /></div>'

            # Modify any POST forms and fix content-length
            body = re.compile(r'(<form\W[^>]*\bmethod=(\'|"|)POST(\'|"|)\b[^>]*>)', re.IGNORECASE)
            resp.body = body.sub(add_csrf_field, resp.body)

        return resp(environ, start_response)

# Override the error middleware...
class PyllError(ErrorMiddleware):

    def exception_handler(self, exc_info, environ):
        simple_html_error = False
        if self.xmlhttp_key:
            get_vars = wsgilib.parse_querystring(environ)
            if dict(get_vars).get(self.xmlhttp_key):
                simple_html_error = True
        return handle_exception(
            exc_info, environ['wsgi.errors'],
            html=True,
            debug_mode=self.debug_mode,
            error_email=self.error_email,
            error_log=self.error_log,
            show_exceptions_in_wsgi_errors=self.show_exceptions_in_wsgi_errors,
            error_email_from=self.from_address,
            smtp_server=self.smtp_server,
            smtp_username=self.smtp_username,
            smtp_password=self.smtp_password,
            smtp_use_tls=self.smtp_use_tls,
            error_subject_prefix=self.error_subject_prefix,
            error_message=self.error_message,
            simple_html_error=simple_html_error,
            reporters=self.reporters)
# Handle it...
def handle_exception(exc_info, error_stream, html=True,
                     debug_mode=False,
                     error_email=None,
                     error_log=None,
                     show_exceptions_in_wsgi_errors=False,
                     error_email_from='errors@localhost',
                     smtp_server='localhost',
                     smtp_username=None,
                     smtp_password=None,
                     smtp_use_tls=False,
                     error_subject_prefix='',
                     error_message=None,
                     simple_html_error=False,
                     reporters=None,
                     ):
    """
    For exception handling outside of a web context

    Use like::

        import sys
        import paste
        import paste.error_middleware
        try:
            do stuff
        except:
            paste.error_middleware.exception_handler(
                sys.exc_info(), paste.CONFIG, sys.stderr, html=False)

    If you want to report, but not fully catch the exception, call
    ``raise`` after ``exception_handler``, which (when given no argument)
    will reraise the exception.
    """

    reported = False
    exc_data = collector.collect_exception(*exc_info)
    extra_data = ''
    if error_email:
        rep = reporter.EmailReporter(
            to_addresses=error_email,
            from_address=error_email_from,
            smtp_server=smtp_server,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            smtp_use_tls=smtp_use_tls,
            subject_prefix=error_subject_prefix)
        rep_err = send_report(rep, exc_data, html=html)
        if rep_err:
            extra_data += rep_err
        else:
            reported = True
    if reporters:
        for rep in reporters:
            rep_err = send_report(rep, exc_data, html=html)
            if rep_err:
                extra_data += rep_err
            else:
                ## FIXME: should this be true?
                reported = True
    if error_log:
        rep = reporter.LogReporter(
            filename=error_log)
        rep_err = send_report(rep, exc_data, html=html)
        if rep_err:
            extra_data += rep_err
        else:
            reported = True
    if show_exceptions_in_wsgi_errors:
        rep = reporter.FileReporter(
            file=error_stream)
        rep_err = send_report(rep, exc_data, html=html)
        if rep_err:
            extra_data += rep_err
        else:
            reported = True
    else:
        error_stream.write('Error - %s: %s\n' % (
            exc_data.exception_type, exc_data.exception_value))
    if html:
        if debug_mode and simple_html_error:
            return_error = formatter.format_html(
                exc_data, include_hidden_frames=False,
                include_reusable=False, show_extra_data=False)
            reported = True
        elif debug_mode and not simple_html_error:
            error_html = formatter.format_html(
                exc_data,
                include_hidden_frames=True,
                include_reusable=False)
            head_html = ''
            return_error = error_template(
                head_html, error_html, extra_data)
            extra_data = ''
            reported = True
        else:
            msg = error_message or '''
            An error occurred.  See the error logs for more information.
            (Turn debug on to display exception reports here)
            '''
            return_error = error_template('', msg, '')
    else:
        return_error = None
    if not reported and error_stream:
        err_report = formatter.format_text(exc_data, show_hidden_frames=True)[0]
        err_report += '\n' + '-'*60 + '\n'
        error_stream.write(err_report)
    if extra_data:
        error_stream.write(extra_data)
    return return_error

# TODO: set by config
def send_report(rep, exc_data, html=True):
    try:
        rep.report(exc_data)
    except:
        output = StringIO()
        traceback.print_exc(file=output)
        if html:
            return """
            <p>Additionally an error occurred while sending the %s report:

            <pre>%s</pre>
            </p>""" % (
                cgi.escape(str(rep)), output.getvalue())
        else:
            return (
                "Additionally an error occurred while sending the "
                "%s report:\n%s" % (str(rep), output.getvalue()))
    else:
        return ''

# TODO: Customize and config
def error_template(head_html, exception, extra):
    return '''
<html>
    <head>
        <title>Server Error</title>
    %s
    </head>
    <body>
        <h1>Error</h1>
        <p>There has been an error processing this request. Please try again, or notify the server administrator if the error persists.</p>
    </body>
</html>''' % (head_html)

def make_error_middleware(app, global_conf, **kw):
    return PyllError(app, global_conf=global_conf, **kw)