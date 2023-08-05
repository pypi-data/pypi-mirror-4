import subprocess
import crypt , getpass, pwd, grp

def is_user (username):
    return username in subprocess.check_output("cat /etc/passwd | grep /home | cut -f1 -d: | sort", shell=True).split('\n')

def is_group (groupname):
    return groupname in subprocess.check_output("cat /etc/group | grep %s | cut -f1 -d: | sort" % groupname , shell=True).split('\n')

def is_in_group (group, user):
    groups = subprocess.check_output("cat /etc/group | grep %s | sort" % group , shell=True).strip()
    group_details = [line for line in groups.split('\n') if line.split(':')[0] == group][0].split(':')
    if user in group_details[-1].split(","):
        return True
    return False

def getuser_hash (user):
    for line in open("/etc/shadow"):
        if user in line:
            return line.split(":")[1]

def authenticate(user, password):
    shadow_line = getuser_hash(user)
    salt = "$" + shadow_line.split("$")[1] + "$" + shadow_line.split("$")[2] + "$"
    hash = crypt.crypt(password, salt)
    if shadow_line == hash:
        return True
    else:
        return False

def list_users():
    return [p[0] for p in pwd.getpwall() if p[2] >= 1000 and p[0] != "nobody"]
    
def list_groups(condition=None):
    condition = condition or (lambda g: True)
    return [g[0] for g in grp.getgrall() if condition(g[0]) and g[2] >= 1000 and g[0] != "nogroup"]

def list_non_user_groups():
    users = list_users()
    return list_groups(lambda g: g not in users)

def users_in_group(group):
    return [user for user in list_users() if is_in_group(group, user)]

def group_is_empty(group):
    return not users_in_group(group)