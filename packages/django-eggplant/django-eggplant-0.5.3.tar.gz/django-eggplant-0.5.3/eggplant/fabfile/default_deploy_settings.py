
# Copyright 2012 Dian-Je Tsai and Wantoto Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from fabric.api import env
from six import callable

default_settings_file_dir = os.path.dirname(__file__)

# Script setup
VERBOSE = 0
CONFIRM_BEFORE_DEPLOY = True

# Connection settings
USE_SSH_CONFIG = False
WEB_SERVERS = []

# Local source code
SOURCE_ROOT = lambda: os.getcwd()
IGNORE_FILE_LIST = lambda: os.path.join(callable(SOURCE_ROOT) and SOURCE_ROOT() or SOURCE_ROOT, '.gitignore')
PROJECT_SETTINGS = lambda: '%s.settings' % env.project_name
PRODUCTION_SETTINGS = lambda: '%s.production_settings' % env.project_name
CHECK_COMMENTS = True
CHECK_TODO = False
CHECK_NOTE = False
CHECK_FIX_ME = True
COLLECT_STATIC = True
#USE_SYMBOLIC_LINK_SETTINGS =  os.path.islink(project_settings_path

# Remote base
REMOTE_PROJECT_NAME = lambda: env.project_name
RUN_REMOTE_SETUP = False
REMOTE_BASE = '/var/django/apps'
ADDITIONAL_IGNORE_LIST = []
CLEAN_PY_IN_REMOTE = False
CHECK_PIP_REQUIREMENTS = True
COMPILE_PYC = True

# Apache
APACHE_CONF_FILE = lambda: env.project_name
APACHE_CONF_DIR = '/etc/httpd/conf.d'
APACHE_CONF_TEMPLATE_FILENAME = lambda: 'apache.conf.jinja2'
APACHE_CONF_TEMPLATE_PATH = lambda: os.path.join(
    default_settings_file_dir,
    callable(APACHE_CONF_TEMPLATE_FILENAME) and APACHE_CONF_TEMPLATE_FILENAME() or APACHE_CONF_TEMPLATE_FILENAME
)
RESTART_APACHE = False
INSTALL_APACHE_CONF = True
UPDATE_APACHE_CONF = False

# MOD_WSGI
AWS_S3_BASE_URL = None
MEDIA_URL = '/media/'
REDIRECT_STATIC_TO_S3 = False
STATIC_URL = '/static/'
SERVE_FAVICON = False
SERVE_MEDIA = False
SERVE_ROBOTS = False
SERVE_STATIC = True
URL_PREFIX = '/'
WSGI_SCRIPT_FILE_NAME = 'wsgi.py'
WSGI_PROCESS_GROUP = 'apache'
WSGI_PROCESS_NAME = lambda: env.project_name
WSGI_PROCESS_USER = 'apache'
WSGI_PROCESSES_COUNT = 2
WSGI_PYTHON_OPTIMIZE_LEVEL = 1
WSGI_THREADS_COUNT = 15
#MEDIA_PATH = os.path.join(remote_project_source_root, 'media')
#STATIC_PATH = os.path.join(remote_project_source_root, 'static')
#VIRTUALENV_SITE_PACKAGES_PATH = os.path.join(remote_project_venv, 'lib/python%s/site-packages')  # Python ver
