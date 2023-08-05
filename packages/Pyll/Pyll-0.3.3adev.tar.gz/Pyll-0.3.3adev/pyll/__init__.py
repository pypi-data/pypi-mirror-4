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


import pkg_resources
from paste.registry import StackedObjectProxy
from paste.config import DispatchingConfig


__all__ = ['app_globals', 'cache', 'config', 'request', 'response',
           'session', 'tmpl_context', 'url']


app_globals = StackedObjectProxy(name="app_globals")
cache = StackedObjectProxy(name="cache")
request = StackedObjectProxy(name="request")
response = StackedObjectProxy(name="response")
session = StackedObjectProxy(name="session")
tmpl_context = StackedObjectProxy(name="tmpl_context")
url = StackedObjectProxy(name="url")
template = StackedObjectProxy(name="template")
permissions = StackedObjectProxy(name="permissions")
auth_id = StackedObjectProxy(name="auth_id")
config = DispatchingConfig()




from paste.script import templates
from paste.deploy.converters import asbool
from paste.script.appinstall import Installer
from paste.script.templates import Template, var


vars = [
    templates.var('version', '0.1'),
    templates.var('description', ''),
    templates.var('long_description', ''),
    templates.var('keywords', 'pyll'),
    templates.var('author', ''),
    templates.var('author_email', ''),
    templates.var('url', ''),
    templates.var('license_name', ''),
    templates.var('zip_safe', 'True/False: if the package can be distributed as a .zip file',
        default=True),
    ]

class PyllTemplate(templates.Template):

    egg_plugins = ['Pyll']
    summary = 'Template system for creating Pyll web framework applications.'
    required_templates = ['basic_package']
    _template_dir = 'templates'
    use_cheetah = False
    vars=vars
