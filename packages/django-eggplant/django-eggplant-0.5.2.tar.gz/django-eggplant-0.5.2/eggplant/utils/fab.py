from fabric.api import local, prefix

def lsudo(command, capture=False):
    return local('sudo %s'%command, capture=capture)

def virtual_env(venv_path):
    return prefix('source %s/bin/activate'%venv_path)

def fab_argument(raw_value):
    try:
        if '.' in raw_value:
            return float(raw_value)
        return int(raw_value)
    except ValueError:
        if raw_value=='True':
            return True
        elif raw_value=='False':
            return False

        return raw_value
