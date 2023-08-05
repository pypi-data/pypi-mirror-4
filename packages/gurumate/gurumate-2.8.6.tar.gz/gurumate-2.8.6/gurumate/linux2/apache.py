import os
def is_module_enabled(mod_name):
    return os.path.isfile("/etc/apache2/mods-enabled/%s.load" % mod_name)
def is_recently_restarted():
    # quick and dirty solution ... check the log file for the latest restart
    output = os.popen("tail -5 /var/log/apache2/error.log|grep caught").readline()
    if output:
        if output.strip().split(', ')[1] == 'shutting down':
            return True
    else:
        return False
def is_recently_reloaded():
    output = os.popen("tail -6 /var/log/apache2/error.log|grep Graceful").readline()
    if output:
        if output.strip().split(', ')[1] == 'doing restart':
            return True
    else:
        return False
def is_mime_type_enabled(mimetype):
    file_path = '/etc/mime.types'
    line = os.popen("grep %s %s" % (mimetype, file_path)).readline()
    if line: 
        if not line.strip().startswith("#"):
            return True
        else:
            return False
    else:
        return False

def check_apache_running_php():
    output = os.popen("tail -6 /var/log/apache2/error.log|grep PHP").readlines()
    return True if len(output) > 1 else False
    #return (open("/var/log/apache2/error.log").read()).count("Apache/2.2.22 (Ubuntu) PHP/5.3.10-1ubuntu3.4 with Suhosin-Patch configured") > 1
    
