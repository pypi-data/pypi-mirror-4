'''
    Apache Specific Utilities

'''
import gurumate.base
from gurumate.base import fail

def check_running(process_name="apache2"):
    '''
        CHECK if process (default=apache2) is not running
    '''
    if not gurumate.base.get_pid_list(process_name):
        fail("Apache process '%s' doesn't seem to be working" % process_name)
        return False #unreachable
    return True

def check_listening_port(port=80, process_name="apache2"):
    '''
        CHECK if process (default=apache2) is running and listening on port 80
    '''
    if port not in get_listening_ports(process_name):
        fail("Apache is not listening on port %s, \
        maybe you forgot to configure the port? \
        or did you forget to start the service?" % port)
            
def get_listening_ports(process_name="apache2"):
    '''
        returns a list of listening ports for running process (default=apache2)
    '''
    ports = set()
    for _, address_info in gurumate.base.get_listening_ports(process_name):
        ports.add(address_info[1])
    return list(ports)