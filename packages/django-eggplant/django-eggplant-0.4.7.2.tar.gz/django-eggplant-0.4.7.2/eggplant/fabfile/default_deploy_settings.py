"""
Copyright 2012 Dian-Je Tsai and Wantoto Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
# Project Name, Required
PROJECT_NAME = None

# Connections
USE_SSH_CONFIG = False
WEB_SERVERS = []

# Local source code
CHECK_COMMENTS = True
CHECK_TODO = False
CHECK_NOTE = False
CHECK_FIX_ME = True
COLLECT_STATIC = True

# Remote base
RUN_REMOTE_SETUP = False
REMOTE_BASE = '/var/django/apps'
DEPLOY_USER = 'eggplant'
ADDITIONAL_IGNORE_LIST = []
CLEAN_PY_IN_REMOTE = False
CHECK_PIP_REQUIREMENTS = True
APACHE_CONF_DIR = '/etc/httpd/conf.d'
APACHE_CONF_TEMPLATE = None
RESTART_APACHE = False
INSTALL_APACHE_CONF = True
COMPILE_PYC = True

# Behavior
CONFIRM_BEFORE_DEPLOY = True

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
#WSGI_PROCESS_NAME = PROJECT_NAME
WSGI_PROCESS_USER = 'apache'
WSGI_PROCESSES_COUNT = 2
WSGI_PYTHON_OPTIMIZE_LEVEL = 1
WSGI_THREADS_COUNT = 15
