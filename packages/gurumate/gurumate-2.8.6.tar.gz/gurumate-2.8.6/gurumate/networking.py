from socket import socket, gethostname
import psutil
import gurumate

def is_port_accessible(ip, port, timeout=5):
    s = socket()
    s.settimeout(timeout)

    try:
        result = s.connect_ex((ip, port))
        
    except Exception:
        return False
    
    finally:
        s.close()
        
        # When 'result' = 0, connected successfuly
        if not result:
            return True
        
        return False
    
def check_hostname(hostname):
    return hostname == gethostname()
            
def check_localaddress(pname, ip, port):
    pid = gurumate.procs.get_pid(pname)
    p = psutil.Process(pid)
    connection = p.get_connections()
    return connection[0].local_address == (str(ip), port)
