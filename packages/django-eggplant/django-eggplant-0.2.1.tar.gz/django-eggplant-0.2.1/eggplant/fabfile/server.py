from fabric.api import abort, env, sudo, execute, puts
from fabric.colors import red
from fabric.decorators import task, roles
from netaddr import IPNetwork
from netaddr.core import AddrFormatError

@task
@roles('web_servers')
def apache(action, load_deploy_settings=False, project_name=None, deploy_settings_path=None):
    """Perform action on apache server
    :param action: action could be ('start', 'stop', 'restart', 'reload', 'status', 'fullstatus')
    """
    if load_deploy_settings:
        execute('deploy_setting', project_name=project_name, deploy_settings_path=deploy_settings_path)
        deploy_settings = env.deploy_settings
        execute(web_server, *deploy_settings.WEB_SERVERS)

    if action not in ('start', 'stop', 'restart', 'reload', 'status', 'fullstatus'):
        abort(red('"%s"' % action, bold=True) + red(' is an invalid action for apache httpd!'))
    sudo('/etc/init.d/httpd %s' % action)

@task
def web_server(*servers):
    """Set targeted web server
    :param servers: list of severs (IP, CIDR, or domain name)
    """
    hosts = []
    for server in servers:
        try:
            hosts += map(lambda x: str(x), list(IPNetwork(server)))
        except (ValueError, AddrFormatError):
            hosts += [server]

    for host in hosts:
        puts('Add "%s" to web server list' % host)

    env.roledefs.update({
        'web_servers': env.roledefs['web_servers'] + hosts
    })
