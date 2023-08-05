import subprocess
import shlex, psutil, socket
from gurumate.exceptions.base import ValidationError, ReturnException, EvalResultException


###### Private Members ########
__version__ = "1.0"

def _iter_processes(process_name):
    for process in psutil.process_iter():
        if process.name == process_name:
            yield process

###### Public API #######
def get_version():
    return __version__

def run_command(command):
    return subprocess.check_output(shlex.split(command))

def get_pid_list(process_name):
    res = []
    for process in _iter_processes(process_name):
        res.append(process.pid)
    return res

def get_listening_ports(process_name):
    ports = [] # (pid, (ip, port))
    for process in _iter_processes(process_name):
        for connection in process.get_connections():
            if connection.status == 'LISTEN':
                ports.append((process.pid, connection.local_address))
    return ports

def get_local_ip(): 
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    ipaddr = s.getsockname()[0]
    return ipaddr

def fail(message):
    raise ValidationError(message)

def fill_template(map):
    raise ReturnException(map)

def ret(status=0, msg=None, metadata=None):
    raise EvalResultException(status, msg, metadata)
