import subprocess
import shlex, re
import os
from subprocess import CalledProcessError
from datetime import *

def find(name):
    '''
        returns a list of tuples (package_name, description) for apt-cache search results
    '''
    cmd = 'apt-cache search %s' % name
    args = shlex.split(cmd)
    try:
        output = subprocess.check_output(args)
    except CalledProcessError:
        return []
    lines = output.splitlines()
    packages = []
    for line in lines:
        package, _, desc = line.partition(' - ')
        packages.append((package, desc)) 
    return packages

def is_installed(name):
    '''
        returns True if package (name) is installed
    '''
    return True if get_installed_version(name) else False

def get_installed_version(name):
    '''
        returns installed package version and None if package is not installed
    '''
    pattern = re.compile(r'''Installed:\s+(?P<version>.*)''')
    cmd = 'apt-cache policy %s' % name
    args = shlex.split(cmd)
    try:
        output = subprocess.check_output(args)
        if not output:
            return None
    except CalledProcessError:
        return None
    # check output
    match = pattern.search(output)
    if match:
        version = match.groupdict()['version']
        if version == '(none)':
            return None
        else:
            return version

def is_partially_installed(filename, final_destination):
    try:
        files = os.popen("ls /var/cache/apt/archives/%s" % filename).readlines()
    except e:
        return False
    if len(files)>0:
        file_path = files[0].rstrip()
        file_installed = os.path.exists(final_destination) 
        return os.path.exists(file_path) and not file_installed
    else:
        return False

def check_in_source_list(source):
    file_path = '/etc/apt/sources.list'
    lines=os.popen("grep %s %s" %(source, file_path)).readlines()
    if len(lines) > 0: # grep has found the source 
        for line in lines:
            if not line.startswith("#"):
                return True
    else:
        return False


def is_recently_updated():
    latest_modification = os.popen("stat /var/lib/apt/lists/ | grep Modify | cut -d: -f2| cut -d \" \" -f2").readline().strip()
    formated_date = latest_modification.split('-')
    modification_datetime = datetime(int(formated_date[0]), int(formated_date[1]), int(formated_date[2]))
    delta = datetime.now() - modification_datetime
    if delta.days > 1:
        return False
    else:
        return True

















    