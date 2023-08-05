import imp
import os
import re
import sys
from fabric.api import (hide, local, env, execute, abort, lcd, sudo, run, cd, puts, settings as fab_settings)
from fabric.colors import red, green, yellow, cyan
from fabric.contrib import django as fab_django
from fabric.contrib.console import confirm
from fabric.contrib.files import upload_template
from fabric.decorators import task, roles
from fabric.state import output as output_level
from fabric.utils import error
from eggplant.utils.fab import lsudo, virtual_env
from eggplant.utils.filesystem import temporary_directory, rsync, render_file

# Set env

env.roledefs.update({
    'web_servers': [],
})

# Private Functions

def deploy_setting(project_name=None, deploy_settings_path=None):
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
        if not os.path.exists(deploy_settings_path): deploy_settings_path = None
    if deploy_settings_path is None and project_name is not None:
        deploy_settings_path = os.path.abspath(os.path.join(os.getcwd(), project_name, 'deploy_settings.py'))
        if not os.path.exists(deploy_settings_path): deploy_settings_path = None
    if deploy_settings_path is None:
        print error(red('Cannot find deploy settings', bold=True))

    # Load deploy_settings
    env.deploy_settings = imp.load_source('', deploy_settings_path)

    # Find project name - 2
    if project_name is None:
        project_name = getattr(env.deploy_settings, 'PROJECT_NAME', None)
    if project_name is None:
        error(red('What is your project name?', bold=True))

    # Load project_name
    env.project_name = project_name

# Tasks

@task
def deploy(project_name=None, deploy_settings_path=None, commit_msg='deploy', verbose=0):
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
    :param verbose:
        Print information or not. Default is 0. Levels=[0, 1, 2, 3]
    """
    # Get deploy settings and project name
    execute(deploy_setting, project_name=project_name, deploy_settings_path=deploy_settings_path)
    project_name = env.project_name
    deploy_settings = env.deploy_settings

    # Check output level
    verbose = int(verbose)
    if verbose==0:
        hide_output_status = ['everything']
    elif verbose==1:
        hide_output_status = ['status', 'stdout', 'stderr']
    elif verbose==2:
        hide_output_status = ['status']
    else:
        hide_output_status = []
    for status in hide_output_status:
        setattr(output_level, status, False)

    # Load ssh config
    env.use_ssh_config = getattr(deploy_settings, 'USE_SSH_CONFIG', False)

    # Load web servers
    if len(env.roledefs['web_servers'])==0:
        with hide('everything'):
            execute('web_server', *getattr(deploy_settings, 'WEB_SERVERS', []))
            if verbose!=0: puts('')

    with temporary_directory(prefix='deploy~%s~'%project_name) as tmp_directory:
        env.tmp_directory = tmp_directory
        # Copy codebase
        puts(cyan('Copy your codebase to temp directory'))
        original_src_root = getattr(deploy_settings, 'SOURCE_ROOT', os.getcwd())
        # Rsync
        copy_codebase_rsync_args = '-a --delete --exclude .git'
        ignore_file_list = getattr(deploy_settings, 'IGNORE_FILE_LIST', os.path.join(original_src_root, '.gitignore'))
        if ignore_file_list is not None and os.path.exists(ignore_file_list):
            copy_codebase_rsync_args += ' --exclude-from \'%s\''%os.path.relpath(ignore_file_list, os.getcwd())
        if not original_src_root.endswith('/'): original_src_root += '/'
        local('rsync %s %s %s'%(
            copy_codebase_rsync_args,
            original_src_root + ('' if original_src_root.endswith('/') else '/'),
            tmp_directory
            )
        )
        # Set project source root and append to PYTHONPATH
        env.project_src_root = project_src_root = tmp_directory
        sys.path = [project_src_root] + sys.path
        if verbose!=0: puts('')

        with lcd(tmp_directory):
            # Switch settings
            project_settings_module = getattr(deploy_settings, 'PROJECT_SETTINGS', '%s.settings'%project_name)
            project_settings_path = project_settings_module.replace('.', '/')+'.py'
            # Use symbolic link or not?
            use_symbolic_link_settings = getattr(
                deploy_settings, 'USE_SYMBOLIC_LINK_SETTINGS', os.path.islink(project_settings_path)
            )
            if use_symbolic_link_settings:
                # Relink to production one
                puts(cyan('Move to production settings'))
                production_settings_module = getattr(
                    deploy_settings, 'PRODUCTION_SETTINGS', '%s.production_settings'%project_name
                )
                production_settings_path = production_settings_module.replace('.', '/')+'.py'
                local('rm -rf %s'%project_settings_path)
                local('ln -s %s %s'%(
                    os.path.relpath(production_settings_path, os.path.dirname(project_settings_path)),
                    project_settings_path
                    )
                )

            # load django in
            fab_django.settings_module(project_settings_module)
            from django.conf import settings as django_settings
            from django.core.management import get_commands
            env.django_settings = django_settings

            # Set paths
            remote_base_path = getattr(deploy_settings, 'REMOTE_BASE', '/var/www/django')
            env.remote_base_path = remote_base_path

            # Get Project Information
            print ''
            print cyan('Project Information:')
            print 'Project Name:    '+green(project_name)
            print 'Deploy Target:'
            print '    Host:      '+yellow(', '.join(env.roledefs['web_servers']))
            print '    Path:      '+yellow(remote_base_path)
            print 'Database: (default one)'
            print '    Engine:    '+yellow(django_settings.DATABASES['default']['ENGINE'])
            print '    Name:      '+yellow(django_settings.DATABASES['default']['NAME'])
            print '    Host:      '+yellow(django_settings.DATABASES['default']['HOST'] or 'localhost')
            print '    User:      '+yellow(django_settings.DATABASES['default']['USER'])
            print ''

            # Check TODOs and FIX_MEs
            if getattr(deploy_settings, 'CHECK_COMMENTS', True):
                print cyan('Check comment in source code')
                check_todo = getattr(deploy_settings, 'CHECK_TODO', False)
                check_note = getattr(deploy_settings, 'CHECK_NOTE', False)
                check_fix_me = getattr(deploy_settings, 'CHECK_FIX_ME', True)
                comment_types = []
                if check_todo: comment_types += ['TODO']
                if check_note: comment_types += ['NOTE']
                if check_fix_me: comment_types += ['FIXME']
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
                            grep_commands += ["grep '%s' -n -r %s --include=%s"%(
                                comment_string, project_src_root, file_type
                            )]
                comment_search_results = []
                for grep_command in grep_commands:
                    local_results = []
                    with fab_settings(hide('everything'), warn_only=True):
                        result = local(grep_command, capture=True)
                        if len(result): local_results += [result]
                    for raw_result in local_results:
                        result_components = raw_result.split(':')
                        path = os.path.relpath(result_components[0], project_src_root)
                        line_number = result_components[1]
                        content = ':'.join(result_components[2:]).strip()
                        comment_search_results += [(path, line_number, content)]
                for path, line_number, content in comment_search_results:
                    print 'Line %s at %s: %s'%(yellow(line_number), yellow(path, bold=True), content)
                if len(comment_search_results)==0:
                    print 'No comment mentioned about %s'%comment_types
                print ''

            # Ask
            if getattr(deploy_settings, 'CONFIRM_BEFORE_DEPLOY', True):
                try:
                    if not confirm('deploy?', default=False):
                        raise KeyboardInterrupt
                except KeyboardInterrupt:
                    abort(red('User cancels deployment ...', bold=True))
                print ''

            # Replace gitignore. We wanna preserve pyc
            project_src_root_gitignore = os.path.join(project_src_root, '.gitignore')
            pyc_pattern = re.compile(r'.*\.py[c|o]$')
            gitignores = []
            with open(project_src_root_gitignore, 'r') as f:
                raw_gitignores = f.read().strip().split('\n')
            for gitignore_item in raw_gitignores:
                if pyc_pattern.match(gitignore_item) is None:
                    gitignores += [gitignore_item]
            gitignores += getattr(deploy_settings, 'ADDITIONAL_IGNORE_LIST', [])
            gitignores += [
                'logs/',
            ]
            gitignores = set([item for item in gitignores if item])
            processed_gitignore_content = '\n'.join(list(set(gitignores)))+'\n'
            with open(project_src_root_gitignore, 'w') as f:
                f.write(processed_gitignore_content)

            # Compile static
            if getattr(deploy_settings, 'COLLECT_STATIC', True):
                puts(cyan('Compile static files'))
                with lcd(project_src_root):
                    if 'collectstatic' in get_commands():
                        local('python manage.py collectstatic --noinput -v 0')
                    if 'compress' in get_commands():
                        # django-compressor
                        local('python manage.py compress')
                if verbose!=0: puts('')

            # Make WSGI
            if getattr(deploy_settings, 'USE_MOD_WSGI', True):
                puts(cyan('Generate configuration file of mod_wsgi and Apache'))
                # Get Apache conf template
                apache_conf_template_filename = 'apache.conf.jinja2'
                apache_conf_template_path = getattr(deploy_settings, 'APACHE_CONF_TEMPLATE', None)
                if apache_conf_template_path is None:
                    apache_conf_template_path = os.path.join(
                        project_src_root,
                        os.path.dirname(project_settings_path),
                        apache_conf_template_filename
                    )
                if not os.path.exists(apache_conf_template_path):
                    apache_conf_template_path = os.path.join(
                        os.path.dirname(__file__),
                        'deploy/%s'%apache_conf_template_filename
                    )
                # Make context for apache conf
                source_root_name = env.source_root_name = 'source'
                venv_name = env.venv_name = 'venv'
                remote_project_path = env.remote_project_path = os.path.join(remote_base_path, project_name)
                remote_project_source_root = env.remote_project_source_root = \
                    os.path.join(remote_project_path, source_root_name)
                remote_project_venv = env.remote_project_venv = os.path.join(remote_project_path, venv_name)
                python_version = sys.version_info
                default_site_packages = os.path.join(
                    remote_project_venv,
                    'lib/python%s.%s/site-packages'%(python_version[0], python_version[1])
                )
                context_keys = [
                    ('AWS_S3_BASE_URL', None),
                    ('MEDIA_URL', '/media/'),
                    ('MEDIA_PATH', os.path.join(remote_project_source_root, 'media')),
                    ('REDIRECT_STATIC_TO_S3', False),
                    ('STATIC_URL', '/static/'),
                    ('STATIC_PATH', os.path.join(remote_project_source_root, 'static')),
                    ('SERVE_FAVICON', False),
                    ('SERVE_MEDIA', False),
                    ('SERVE_ROBOTS', False),
                    ('SERVE_STATIC', True),
                    ('URL_PREFIX', '/'),
                    ('VIRTUALENV_SITE_PACKAGES_PATH', default_site_packages),
                    ('WSGI_SCRIPT_DIR_NAME', os.path.join(remote_project_source_root, project_name)),
                    ('WSGI_SCRIPT_FILE_NAME', 'wsgi.py'),
                    ('WSGI_PROCESS_GROUP', 'apache'),
                    ('WSGI_PROCESS_NAME', project_name),
                    ('WSGI_PROCESS_USER', 'apache'),
                    ('WSGI_PROCESSES_COUNT', 2),
                    ('WSGI_PYTHON_OPTIMIZE_LEVEL', 1),
                    ('WSGI_THREADS_COUNT', 15),
                ]
                apache_conf_context = {}
                for context_key, context_default_value in context_keys:
                    context_value = getattr(deploy_settings, context_key, context_default_value)
                    apache_conf_context[context_key.lower()] = context_value
                apache_conf_context['project_path'] = remote_project_source_root
                # Render Apache conf
                apache_conf_content = render_file(apache_conf_template_path, apache_conf_context).strip()
                apache_conf_content = re.sub(r'( *\n){2,}', '\n\n', apache_conf_content) + '\n'
                # Write it temporarily
                apache_conf_temp_path = os.path.join(
                    project_src_root,
                    os.path.dirname(project_settings_path),
                    'apache.conf'
                )
                env.tmp_apache_conf_path = os.path.relpath(apache_conf_temp_path, project_src_root)
                with open(apache_conf_temp_path, 'w') as f:
                    f.write(apache_conf_content)

            # Go!
            print cyan('Send codebase to remote servers')
            print 'Remote: %s'%env.roledefs['web_servers']
            if verbose!=0: puts('')
            # Save arguments
            env.commit_msg = commit_msg
            execute(deploy_to_remote)

            # Clean up
            print green('Deploy finished', bold=True)

@roles('web_servers')
def deploy_to_remote():
    """
    This is the private core task who really do deploy to web servers.
    Call "deploy" task. Don't call this directly.
    """
    # Get variables
    deploy_settings = env.deploy_settings
    project_name = env.project_name
    project_src_root = env.project_src_root
    remote_base_path = env.remote_base_path
    host_string = env.host_string
    commit_msg = env.commit_msg

    # Define function callee
    host_name = host_string.split('@')[-1]
    use_sudo = getattr(deploy_settings, 'USE_SUDO_IN_REMOTE', True)
    if host_name in ('127.0.0.1', 'localhost'):
        # run
        if use_sudo: target_run = lsudo
        else: target_run = local
        # sudo
        target_sudo = lsudo
        # cd
        target_cd = lcd
    else:
        # run
        if use_sudo: target_run = sudo
        else: target_run = run
        # sudo
        target_sudo = sudo
        # cd
        target_cd = cd

    puts(green('Deploy to %s'%host_string))

    # Make room for deploy target
    puts('Deploy target is: %s'%remote_base_path)
    if not os.path.exists(remote_base_path):
        puts(yellow('Deploy target doesn\'t exist. Create one now. (The target will be cleaned if existed)'))
        target_run('mkdir -p %s'%remote_base_path)
        target_run('chmod o+rx %s'%remote_base_path)

    # Make room for your project
    source_root_name = env.source_root_name
    remote_project_path = env.remote_project_path
    remote_project_source_root = env.remote_project_source_root
    remote_project_venv = env.remote_project_venv

    # Init project
    if not os.path.exists(remote_project_path):
        puts(yellow('First time deploy, create git repository:'))
        # Make room
        target_run('mkdir -p %s'%remote_project_path)
        # Source folder with git
        target_run('mkdir -p %s'%remote_project_source_root)
        with target_cd(remote_project_path):
            target_run('git init')
            target_run('touch .gitignore')
            target_run('git add .gitignore && git commit -m "Init commit"')
        # Virtualenv
        puts(yellow('First time deploy, initialize virtualenv:'))
        with target_cd(remote_project_path):
            target_run('virtualenv venv')

    # Send codebase
    puts(cyan('Copy project codebase to remote'))
    rsync_argument = '-DLprtz --delete --delete-excluded --exclude \'*.pyc\' --exclude-from \'.gitignore\''
    local(rsync(
        project_src_root + ('' if project_src_root.endswith('/') else '/'),
        remote_project_source_root,
        rsync_argument=rsync_argument
    ))

    # Copy gitignore
    with target_cd(remote_project_path):
        target_run(rsync('source/.gitignore', '.gitignore'))

    # Install venv
    if getattr(deploy_settings, 'CHECK_PIP_REQUIREMENTS', True):
        puts(cyan('Install virtualenv for your project'))
        with fab_settings(virtual_env(remote_project_venv)):
            target_run('pip install -r %s/requirements.txt --upgrade' % source_root_name)

    # Compile python
    if getattr(deploy_settings, 'COMPILE_PYC', True):
        clean_py = getattr(deploy_settings, 'CLEAN_PY_IN_REMOTE', False)
        puts(cyan('Compile to Python bytecode: ') + '%s'%remote_project_source_root)
        target_run('python -m compileall -q %s'%remote_project_source_root)
        if clean_py:
            target_run('find %s -name \'*.py\' -exec rm -rf {} \;'%remote_project_source_root)

    # Update settings and commit git
    puts(cyan('Update project record and commit repository'))
    with fab_settings(target_cd(remote_project_path), hide('warnings'), warn_only=True):
        target_run('git add -A && git commit -m "%s"'%commit_msg)

    # Install apache conf
    if getattr(deploy_settings, 'USE_MOD_WSGI', True):
        puts(cyan('Install Apache configuration file'))
        apache_conf_source = os.path.join(remote_project_source_root, env.tmp_apache_conf_path)
        apache_conf_target = getattr(deploy_settings, 'APACHE_CONF_DIR', '/etc/httpd/conf.d/')
        target_run('cp %s %s'%(apache_conf_source, apache_conf_target))

    if getattr(deploy_settings, 'RESTART_APACHE', True):
        puts(cyan('Restarting Apache HTTP Server'))
        target_sudo('/etc/init.d/httpd restart')

    print ''
