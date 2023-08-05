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
        execute('load_deploy_setting', project_name=project_name, deploy_settings_path=deploy_settings_path)
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

    user_hosts = []
    for host in hosts:
        puts('Add "%s" to web server list' % host)
        user_hosts.append('eggplant@%s' % host)

    env.roledefs.update({
        'web_servers': env.roledefs['web_servers'] + user_hosts
    })


@task
def setup(target_server):
    print target_server
