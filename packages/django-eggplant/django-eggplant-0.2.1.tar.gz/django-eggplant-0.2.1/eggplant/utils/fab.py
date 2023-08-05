from fabric.api import local, prefix

def lsudo(command, capture=False):
    return local('sudo %s'%command, capture=capture)

def virtual_env(venv_path):
    return prefix('source %s/bin/activate'%venv_path)