
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

import datetime
import os
import sys
from fabric.api import (hide, local, env, execute, abort, lcd, sudo, run, cd, puts, settings as fab_settings,
                        quiet, prompt, get)
from fabric.colors import red, green, yellow, cyan
from fabric.contrib import django as fab_django
from fabric.contrib.console import confirm
from fabric.contrib.files import exists as remote_exists, append as remote_append
from fabric.decorators import task, roles
from fabric.state import output as output_level
from fabric.utils import error
import yajl as json

from eggplant.utils import SettingsDict
from eggplant.utils.fab import lsudo, virtual_env, fab_argument
from eggplant.utils.filesystem import temporary_directory, rsync, render_file

# Set env

env.roledefs.update({
    'web_servers': [],
})

# Private Functions


def deploy_setting(project_name=None, deploy_settings_path=None, **setting_patches):
    """Get deploy_settings.

    This method will be called by deploy task.
    If you defined one of project_name and deploy_settings in fabric's env, you don't have to call this.
    If you don't define it, call this before execute deploy task.
    You must set one of the 2 arguments when calling this without defining fabric's env.

    :param project_name:
        The name of project. You can also set it in fabric's env.
    :param deploy_settings_path:
        The path of deploy_settings from a path in PYTHONPATH.
        You can also set it in fabric's env.
    """
    # Find project name - 1
    if project_name is None:
        project_name = getattr(env, 'project_name', None)

    # Find deploy_settings
    if deploy_settings_path is None:
        deploy_settings_path = getattr(env, 'deploy_settings', None)

    if deploy_settings_path is None:
        deploy_settings_path = os.path.abspath(os.path.join(os.getcwd(), 'deploy_settings.py'))
        if not os.path.exists(deploy_settings_path):
            deploy_settings_path = None

    if deploy_settings_path is None and project_name is not None:
        deploy_settings_path = os.path.abspath(os.path.join(os.getcwd(), project_name, 'deploy_settings.py'))
        if not os.path.exists(deploy_settings_path):
            deploy_settings_path = None

    if deploy_settings_path is None:
        print error(red('Cannot find deploy settings', bold=True))

    # Load deploy_settings
    default_deploy_settings_path = os.path.join(os.path.dirname(__file__), 'default_deploy_settings.py')
    if project_name is not None:
        setting_patches.update({'PROJECT_NAME': project_name})
    patches = {}
    for key, value in setting_patches.items():
        patches[key] = fab_argument(value)
    env.deploy_settings = SettingsDict(default_deploy_settings_path, deploy_settings_path, **patches)

    # Find project name - 2
    if project_name is None:
        project_name = getattr(env.deploy_settings, 'PROJECT_NAME', None)
    if project_name is None:
        error(red('What is your project name?', bold=True))

    # Load project_name
    env.project_name = project_name


def load_web_servers():
    if len(env.roledefs['web_servers']) == 0:
        with hide('everything'):
            execute('server.web_server', *env.deploy_settings.get('WEB_SERVERS'))
            verbose = env.deploy_settings.get('VERBOSE')
            if verbose != 0:
                puts('')
    if len(env.roledefs['web_servers']) == 0:
        abort('Where do you want to deploy to?')

# Tasks


@task
def add_user(role='web_servers', project_name=None, deploy_settings_path=None, **additional_settings):
    """Add current user to remote server
    """
    ssh_key_path = prompt('Path of your ssh public key: ', default='~/.ssh/id_rsa.pub')
    ssh_key_path = os.path.abspath(os.path.expanduser(ssh_key_path))

    if not os.path.exists(ssh_key_path):
        abort('No file found at %s' % ssh_key_path)

    execute(
        deploy_setting, project_name=project_name, deploy_settings_path=deploy_settings_path, **additional_settings
    )
    execute(load_web_servers)

    ssh_home_path = '~/.ssh'
    ssh_authorized_keys_path = '%s/authorized_keys' % ssh_home_path
    with open(ssh_key_path, 'r') as f:
        ssh_key = f.read().strip()

    print ''

    @roles(role)
    def core():
        # Create ssh home
        if not remote_exists(ssh_home_path):
            run('mkdir -p %s' % ssh_home_path)
            run('chmod 700 %s' % ssh_home_path)
        if not remote_exists(ssh_authorized_keys_path):
            run('touch %s' % ssh_authorized_keys_path)
            run('chmod 644 %s' % ssh_authorized_keys_path)

        with temporary_directory(prefix='add_deploy_user~%s~' % project_name) as tmp_directory:
            local_authorized_keys_path = os.path.join(tmp_directory, 'remote_authorized_keys')
            # Get remote key
            with hide('everything'):
                get(ssh_authorized_keys_path, local_authorized_keys_path)
            with open(local_authorized_keys_path, 'r') as local_authorized_keys:
                for authorized_key in local_authorized_keys:
                    if authorized_key.strip() == ssh_key:
                        print cyan('You have been here.')
                        return

        remote_append(ssh_authorized_keys_path, ssh_key)
        print green('You have joined here.')

    with fab_settings():
        execute(core)


@task
def setup_server():
    if env.host_string is None:
        abort('Assign a target server you can reach')

    # Do you have user "eggplant"?
    with fab_settings(hide('everything'), warn_only=True):
        has_eggplant_user = run('egrep ^eggplant: /etc/passwd').return_code == 0
    if not has_eggplant_user:
        print cyan('Create user ') + cyan('"eggplant"', bold=True)
        sudo('useradd eggplant')
        sudo('passwd eggplant')
        sudo('usermod -a -G wheel eggplant')

    execute(add_user)


@task(default=True)
def deploy(project_name=None, deploy_settings_path=None, commit_msg='deploy', **additional_settings):
    """Deploy current django project to targeted web servers

    This is a public task. It will prepare arguments for the
    core task "deploy_to_remote" which is a private task.

    :param project_name:
        The name of project. If you don't specify this, eggplant will find in following locations until found:

        1. 'env' of current fabric context (env.project_name = <PROJECT_NAME>)
        2. 'deploy_settings.py' (If "deploy_settings.py" can be found without "project_name")

    :param deploy_settings_path:
        The location of "deploy_settings.py". If you don't specify this,
        eggplant will find in following ways until found:

        1. 'env' of current fabric context (env.deploy_settings = <DEPLOY_SETTING_MODULE>)
        2. <CURRENT_WORKING_DIRECTORY>/deploy_settings.py
        3. <CURRENT_WORKING_DIRECTORY>/<PROJECT_NAME>/deploy_settings.py
            (If 'project_name' is specified or can be found without deploy_settings)

    :param commit_msg:
        The message used for git commit in deploy target
    :param update_apache_conf:
        Update Apache configuration file or not.
        If this is first-time deploy, the value will be forced to True.
    """
    # TODO: Create database if not exists

    # Get deploy settings and project name
    global gitignores, pyc_pattern, raw_gitignores, project_src_root_gitignore
    execute(
        deploy_setting, project_name=project_name, deploy_settings_path=deploy_settings_path, **additional_settings
    )
    project_name = env.project_name
    deploy_settings = env.deploy_settings
    env.update_apache_conf = deploy_settings.get('UPDATE_APACHE_CONF')

    # Check output level
    env.verbose = verbose = deploy_settings.get('VERBOSE')
    if verbose == 0:
        hide_output_status = ['everything']
    elif verbose == 1:
        hide_output_status = ['status', 'stdout', 'stderr']
    elif verbose == 2:
        hide_output_status = ['status']
    else:
        hide_output_status = []
    for status in hide_output_status:
        setattr(output_level, status, False)

    # Load ssh config
    env.use_ssh_config = deploy_settings.get('USE_SSH_CONFIG')

    # Load web servers
    execute(load_web_servers)

    with temporary_directory(prefix='deploy~%s~' % project_name) as tmp_directory:
        env.tmp_directory = tmp_directory
        # Copy codebase
        puts(cyan('Copy your codebase to temp directory'))
        original_src_root = deploy_settings.get('SOURCE_ROOT')

        # Project settings module
        project_settings_module = deploy_settings.get('PROJECT_SETTINGS')
        env.project_settings_path = project_settings_path = project_settings_module.replace('.', '/') + '.py'
        # Use symbolic link or not?
        use_symbolic_link_settings = deploy_settings.get(
            'USE_SYMBOLIC_LINK_SETTINGS', os.path.islink(project_settings_path)
        )

        # Rsync
        copy_codebase_rsync_args = '-DLprtza --delete --exclude .git'
        ignore_file_list = os.path.abspath(deploy_settings.get('IGNORE_FILE_LIST'))
        if ignore_file_list is not None and os.path.exists(ignore_file_list):
            copy_codebase_rsync_args += ' --exclude-from \'%s\'' % os.path.relpath(ignore_file_list, os.getcwd())
        if not original_src_root.endswith('/'):
            original_src_root += '/'
        local('rsync %s %s %s' % (
            copy_codebase_rsync_args, original_src_root + ('' if original_src_root.endswith('/') else '/'),
            tmp_directory))
        # Replace original git-ignore ...
        # Original git-ignore is used for SCM repository.
        # Now we need here is for remote base, so we copied/replaced the SCM one with IGNORE_FILE_LIST
        if ignore_file_list is not None and os.path.exists(ignore_file_list):
            target_gitignore = os.path.join(tmp_directory, '.gitignore')
            copy_gitignore = False
            if not os.path.exists(target_gitignore):
                copy_gitignore = True
            # Copy only if they are different
            with quiet():
                diff_result = local('diff %s %s' % (ignore_file_list, target_gitignore))
                if diff_result.return_code == 1:
                    copy_gitignore = True
            if copy_gitignore:
                local(rsync(ignore_file_list, target_gitignore))

        # Set project source root and append to PYTHONPATH
        env.project_src_root = project_src_root = tmp_directory
        sys.path = [project_src_root] + sys.path
        if verbose != 0:
            puts('')

        with lcd(tmp_directory):
            # Switch settings
            if use_symbolic_link_settings:
                # Relink to production one
                puts(cyan('Move to production settings'))
                production_settings_module = deploy_settings.get('PRODUCTION_SETTINGS')
                production_settings_path = production_settings_module.replace('.', '/') + '.py'
                local('rm -rf %s' % project_settings_path)
                local('ln -s %s %s' % (
                    os.path.relpath(production_settings_path, os.path.dirname(project_settings_path)),
                    project_settings_path)
                )

            # load django in
            fab_django.settings_module(project_settings_module)
            from django.conf import settings as django_settings
            from django.core.management import get_commands
            env.django_settings = django_settings  #TODO: load which one?

            # Set paths
            remote_base_path = deploy_settings.get('REMOTE_BASE')
            env.remote_base_path = remote_base_path

            # Get Project Information
            print ''
            print cyan('Project Information:')
            print 'Project Name:    ' + green(project_name)
            print 'Deploy Target:'
            print '    Host:      ' + yellow(', '.join(env.roledefs['web_servers']))
            print '    Path:      ' + yellow(remote_base_path)
            print 'Database: (default one)'
            print '    Engine:    ' + yellow(django_settings.DATABASES['default']['ENGINE'])
            print '    Name:      ' + yellow(django_settings.DATABASES['default']['NAME'])
            if 'HOST' in django_settings.DATABASES['default']:
                print '    Host:      ' + yellow(django_settings.DATABASES['default']['HOST'] or 'localhost')
            print '    User:      ' + yellow(django_settings.DATABASES['default']['USER'])
            print ''

            # Check TODOs and FIX_MEs
            if deploy_settings.get('CHECK_COMMENTS'):
                print cyan('Check comment in source code')
                check_todo = deploy_settings.get('CHECK_TODO')
                check_note = deploy_settings.get('CHECK_NOTE')
                check_fix_me = deploy_settings.get('CHECK_FIX_ME')
                comment_types = []
                if check_todo:
                    comment_types += ['TODO']
                if check_note:
                    comment_types += ['NOTE']
                if check_fix_me:
                    comment_types += ['FIXME']
                grep_commands = []
                comment_styles = [
                    ('# %s:', ['*.py', ]),
                    ('<!-- %s:', ['*.html', ]),
                    ('// %s:', ['*.less', '*.js']),
                    ('/\* %s:', ['*.css', ]),
                ]
                for comment_type in comment_types:
                    for comment_style, file_types in comment_styles:
                        for file_type in file_types:
                            comment_string = comment_style % comment_type
                            grep_commands += [
                                "grep '%s' -n -r %s --include=%s" % (comment_string, project_src_root, file_type)
                            ]
                comment_search_results = []
                for grep_command in grep_commands:
                    local_results = []
                    with fab_settings(hide('everything'), warn_only=True):
                        result = local(grep_command, capture=True)
                        if len(result):
                            local_results += [result]
                    for raw_result in local_results:
                        result_components = raw_result.split(':')
                        path = os.path.relpath(result_components[0], project_src_root)
                        line_number = result_components[1]
                        content = ':'.join(result_components[2:]).strip()
                        comment_search_results += [(path, line_number, content)]
                for path, line_number, content in comment_search_results:
                    print 'Line %s at %s: %s' % (yellow(line_number), yellow(path, bold=True), content)
                if len(comment_search_results) == 0:
                    print 'No comment mentioned about %s' % comment_types
                print ''

            # Ask
            if deploy_settings.get('CONFIRM_BEFORE_DEPLOY'):
                try:
                    if not confirm('deploy?', default=False):
                        raise KeyboardInterrupt
                except KeyboardInterrupt:
                    abort(red('User cancels deployment ...', bold=True))
                print ''

            # Replace gitignore. We wanna preserve pyc
            project_src_root_gitignore = os.path.join(project_src_root, '.gitignore')
            gitignores = []
            with open(project_src_root_gitignore, 'r') as f:
                raw_gitignores = f.read().strip().split('\n')
            for gitignore_item in raw_gitignores:
                if gitignore_item not in ('*.pyc', '*.pyo', '*.py[co]'):
                    gitignores += [gitignore_item]
            gitignores += deploy_settings.get('ADDITIONAL_IGNORE_LIST')
            gitignores += [
                'logs/',
            ]
            gitignores = set([item for item in gitignores if item])
            processed_gitignore_content = '\n'.join(list(set(gitignores))) + '\n'
            with open(project_src_root_gitignore, 'w') as f:
                f.write(processed_gitignore_content)

            # Compile static
            if deploy_settings.get('COLLECT_STATIC'):
                puts(cyan('Compile static files'))
                with lcd(project_src_root):
                    if 'collectstatic' in get_commands() and \
                       'django.contrib.staticfiles' in django_settings.INSTALLED_APPS:
                        local('python manage.py collectstatic --noinput -v 0')
                    if 'compress' in get_commands() and 'compressor' in django_settings.INSTALLED_APPS:
                        # django-compressor
                        local('python manage.py compress')
                if verbose != 0:
                    puts('')

            # Go!
            print cyan('Send codebase to remote servers')
            print 'Remote: %s' % env.roledefs['web_servers']
            print ''
            # Save arguments
            env.commit_msg = commit_msg
            execute(deploy_to_remote)

            # Clean up
            print green('Deploy finished', bold=True)


@roles('web_servers')
def deploy_to_remote():
    """This is the private core task who really do deploy to web servers.
    Call "deploy" task. Don't call this directly.
    """
    # local inner function
    def print_title(title):
        if verbose == 0:
            print title
        else:
            print cyan(title)

    # Get variables
    remote_base_path = env.remote_base_path
    deploy_settings = env.deploy_settings
    project_name = env.project_name
    source_root_name = 'source'
    venv_name = 'venv'
    log_name = 'logs'
    remote_project_path = os.path.join(remote_base_path, deploy_settings.get('REMOTE_PROJECT_NAME'))
    remote_project_source_root = env.remote_project_source_root = os.path.join(remote_project_path, source_root_name)
    remote_project_venv = env.remote_project_venv = os.path.join(remote_project_path, venv_name)
    remote_project_log_root = env.remote_project_log_root = os.path.join(remote_project_path, log_name)
    project_src_root = env.project_src_root
    host_string = env.host_string
    commit_msg = env.commit_msg
    verbose = env.verbose
    host_name = host_string.split('@')[-1]
    project_settings_path = env.project_settings_path
    update_apache_conf = env.update_apache_conf

    # Update environment
    env['shell_env'] = deploy_settings.get('REMOTE_ENVIRONMENTS')

    # Define function to call
    if host_name in ('127.0.0.1', 'localhost'):
        is_remote = False
        capture_output = {'capture': True}
        target_run = local
        # sudo
        target_sudo = lsudo
        # cd
        target_cd = lcd
        # file existence
        target_file_existence = os.path.exists
    else:
        is_remote = True
        capture_output = {}
        target_run = run
        # sudo
        target_sudo = sudo
        # cd
        target_cd = cd
        # file existence
        target_file_existence = remote_exists

    # Get eggplant settings in server
    eggplant_server_setting = {}
    with fab_settings(hide('everything'), warn_only=True):
        eggplant_server_settings = target_run('cat /etc/eggplant.conf', **capture_output)
        if eggplant_server_settings.return_code != 0:
            eggplant_server_settings = '{}'
        try:
            eggplant_server_setting.update(json.loads(eggplant_server_settings))
        except ValueError:
            raise ValueError('Error eggplant configuration')

    print(yellow('Deploy to %s' % host_string, bold=True))

    # Update YUM?
    if deploy_settings.get('UPDATE_YUM_PACKAGES'):
        print_title('Update Yum Packages')
        allow_yum = eggplant_server_setting.get('ALLOW_YUM_UPDATE', True)
        with fab_settings(hide('everything'), warn_only=True):
            has_yum = target_run('which yum', **capture_output).return_code == 0
        yum_packages = deploy_settings.get('YUM_PACKAGES')
        if allow_yum and has_yum and len(yum_packages) != 0:
            yum_package_string = ' '.join(yum_packages)
            print(yellow('Updating yum packages'))
            target_sudo('yum install -y %s' % yum_package_string)

    # Make room for deploy target
    puts('Deploy target is: %s' % remote_base_path)
    if not target_file_existence(remote_base_path):
        print(yellow('Deploy target doesn\'t exist. Create one now.'))
        target_sudo('mkdir -p %s' % remote_base_path)
        target_sudo('chmod o+rx %s' % remote_base_path)

    # Init project
    if not target_file_existence(remote_project_path):
        print(yellow('First time deploy, create git repository:'))
        update_apache_conf = True
        # Make room
        target_sudo('mkdir -p %s' % remote_project_path)
        target_sudo('mkdir -p %s' % remote_project_log_root)
        target_sudo('chown -R eggplant:eggplant %s' % remote_project_path)
        # Source folder with git
        target_run('mkdir -p %s' % remote_project_source_root)
        with target_cd(remote_project_path):
            target_run('git init')
            target_run('echo "# ignore files" >> .gitignore')
            target_run('git add .gitignore && git commit -m "Init commit"')
        # Virtualenv
        puts(yellow('First time deploy, initialize virtualenv:'))
        with target_cd(remote_project_path):
            target_run('virtualenv %s' % venv_name)

    # Install apache conf
    wsgi_script_dir_name = os.path.abspath(
        os.path.join(remote_project_source_root, deploy_settings.get('WSGI_SCRIPT_DIR_NAME'))
    )
    wsgi_script_file_name = deploy_settings.get('WSGI_SCRIPT_FILE_NAME')
    apache_conf_tmp_name = 'apache~%s.conf' % host_name
    if deploy_settings.get('INSTALL_APACHE_CONF') and update_apache_conf:
        puts(cyan('Generate configuration file of mod_wsgi and Apache'))
        # Get Apache conf template
        apache_conf_template_filename = deploy_settings.get('APACHE_CONF_TEMPLATE_FILENAME')
        apache_conf_template_path = os.path.join(
            project_src_root,
            os.path.dirname(project_settings_path),
            apache_conf_template_filename
        )
        if not os.path.exists(apache_conf_template_path):
            apache_conf_template_path = deploy_settings.get('APACHE_CONF_TEMPLATE_PATH')
        # Make context for apache conf
        with hide('everything'):
            raw_python_version = target_run('python -c "import sys; print sys.version_info"', **capture_output)
            python_version = map(lambda x: x.strip().replace('\'', ''), raw_python_version[1:-1].split(','))
        default_site_packages = os.path.join(
            remote_project_venv,
            'lib/python%s.%s/site-packages' % (python_version[0], python_version[1])
        )
        apache_conf_context_keys = [
            ('AWS_S3_BASE_URL',),
            ('MEDIA_URL',),
            ('MEDIA_PATH', os.path.join(remote_project_source_root, 'media')),
            ('REDIRECT_STATIC_TO_S3',),
            ('STATIC_URL',),
            ('STATIC_PATH', os.path.join(remote_project_source_root, 'static')),
            ('SERVE_FAVICON',),
            ('SERVE_MEDIA',),
            ('SERVE_ROBOTS',),
            ('SERVE_STATIC',),
            ('URL_PREFIX',),
            ('VIRTUALENV_SITE_PACKAGES_PATH', default_site_packages),
            ('WSGI_PROCESS_GROUP',),
            ('WSGI_PROCESS_NAME',),
            ('WSGI_PROCESS_USER',),
            ('WSGI_PROCESSES_COUNT',),
            ('WSGI_PYTHON_OPTIMIZE_LEVEL',),
            ('WSGI_THREADS_COUNT',),
        ]
        apache_conf_context = {}
        for settings_fetch_args in apache_conf_context_keys:
            context_value = deploy_settings.get(*settings_fetch_args)
            apache_conf_context[settings_fetch_args[0].lower()] = context_value
        apache_conf_context['project_base_path'] = remote_project_path
        apache_conf_context['project_log_path'] = remote_project_log_root
        apache_conf_context['project_source_path'] = remote_project_source_root
        apache_conf_context['wsgi_script_dir_name'] = wsgi_script_dir_name
        apache_conf_context['wsgi_script_file_name'] = wsgi_script_file_name
        # Render Apache conf
        apache_conf_content = render_file(apache_conf_template_path, apache_conf_context, optimize=True)
        apache_conf_tmp_path = os.path.join(project_src_root, apache_conf_tmp_name)
        with open(apache_conf_tmp_path, 'w') as f:
            f.write(apache_conf_content)
        puts('')

    # Send codebase
    print_title('Copy project codebase to remote')
    # Clean old pyc
    target_run('find %s -name \'*.pyc\' -exec rm -rf {} \;' % remote_project_source_root)
    # Do rsync
    rsync_argument = '-DLhrctz --delete --delete-excluded --exclude \'*.pyc\' --exclude-from \'.gitignore\''
    if verbose == 0:
        rsync_argument += ' -q'
    elif verbose == 2:
        rsync_argument += ' -v'
    elif verbose == 3:
        rsync_argument += ' -Pv'
    local(rsync(
        project_src_root + ('' if project_src_root.endswith('/') else '/'),
        (host_string + ':' if is_remote else '') + remote_project_source_root, rsync_argument=rsync_argument))

    # Setup Remote
    if deploy_settings.get('RUN_REMOTE_SETUP'):
        remote_setup_path = deploy_settings.get(
            'REMOTE_SETUP_SCRIPT', os.path.join(remote_project_source_root, project_name, 'remote_setup.py')
        )
        print(cyan('Setup remote'))
        if target_file_existence(remote_setup_path):
            target_run('chmod u+x %s' % remote_setup_path)
            remote_setup_dir, remote_setup_filename = os.path.split(remote_setup_path)
            with target_cd(remote_setup_dir):
                target_run('./%s' % remote_setup_filename)
            target_run('chmod u-x %s' % remote_setup_path)
        else:
            print(yellow('Cannot find remote setup script'))

    # Copy gitignore
    with target_cd(remote_project_path):
        target_run(rsync('%s/.gitignore' % source_root_name, '.gitignore'))

    # Install venv
    if deploy_settings.get('CHECK_PIP_REQUIREMENTS'):
        print_title('Install/Upgrade python packages for your project (virtualenv)')
        with fab_settings(virtual_env(remote_project_venv), target_cd(remote_project_path)):
            target_run('pip install -r %s/requirements.txt' % source_root_name)

    # Add timestamp in wsgi.py
    wsgi_path = os.path.join(wsgi_script_dir_name, wsgi_script_file_name)
    target_run('echo "# " >> %s' % wsgi_path)
    target_run('echo "# Deploy at: %s" >> %s' % (datetime.datetime.now().strftime('%s.%f'), wsgi_path))

    # Compile python
    if deploy_settings.get('COMPILE_PYC'):
        clean_py = deploy_settings.get('CLEAN_PY_IN_REMOTE')
        print_title('Compile Python bytecode')
        target_run('python -m compileall -q %s' % remote_project_source_root)
        if clean_py:
            target_run('find %s -name \'*.py\' -exec rm -rf {} \;' % remote_project_source_root)

    # DB migrate
    with fab_settings(virtual_env(remote_project_venv), target_cd(remote_project_source_root)):
        target_run('python manage.py syncdb --noinput')
        target_run('python manage.py migrate')

    # Install WSGI
    apache_conf_updated = False
    if deploy_settings.get('INSTALL_APACHE_CONF') and update_apache_conf:
        print(cyan('Install apache conf'))
        apache_conf_path = deploy_settings.get('APACHE_CONF_DIR')
        apache_conf_target = os.path.join(apache_conf_path, '%s.conf' % deploy_settings.get('APACHE_CONF_FILE'))
        print cyan('Installing Apache conf')
        with target_cd(remote_project_source_root):
            target_sudo('mv %s %s' % (apache_conf_tmp_name, apache_conf_target))
        apache_conf_updated = True

    # Commit git
    puts(cyan('Update project record and commit repository'))
    with fab_settings(target_cd(remote_project_path), hide('warnings'), warn_only=True):
        target_run('git add -A && git commit -m "%s"' % commit_msg)

    if deploy_settings.get('RESTART_APACHE') or apache_conf_updated:
        print(cyan('Restarting Apache HTTP Server'))
        target_sudo('/etc/init.d/httpd restart')

    print ''
