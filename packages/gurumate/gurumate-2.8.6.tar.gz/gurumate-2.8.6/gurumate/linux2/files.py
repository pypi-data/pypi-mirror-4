import os
import stat
import pwd
import ConfigParser
import re
import time
from gurumate.base import fail
from stat import *
from pwd import getpwuid

def check_isfile(filepath):
    try:
        st = os.stat(filepath)
    except OSError:
        fail("no file named (%s) in the system" % filepath)

    if not stat.S_ISREG(st.st_mode):
        fail("%s is not a regular file." % filepath)
        
    
def check_isdir(dirpath):
    try:
        st = os.stat(dirpath)
    except OSError:
        fail("no directory named (%s) in the system" % dirpath)

    if not stat.S_ISDIR(st.st_mode):
        fail("%s is not a directory." % dirpath)
        
def check_readaccess(filepath, user_name):
    try:
        st = os.stat(filepath)
    except OSError:
        fail("no file named (%s) in the system" % filepath)
        
    mode = st.st_mode    
    # Others
    if mode & stat.S_IROTH:
        return
    
    try:
        passdb_entry = pwd.getpwnam(user_name)
    except KeyError:
        fail("no user called (%s) on the system" % user_name)
    user_id = passdb_entry.pw_uid
    group_id = passdb_entry.pw_gid
    
    owner_uid = st.st_uid
    owner_gid = st.st_gid
    
    # Group
    if owner_gid == group_id:
        if mode & stat.S_IRGRP:
            return
    
    # User
    if owner_uid == user_id:
        if mode & stat.S_IRUSR:
            return
    
    fail("user (%s) has no read access on file (%s)" % (user_name, filepath))
    
def check_writeaccess(filepath, user_name):
    try:
        st = os.stat(filepath)
    except OSError:
        fail("no file name (%s) in the system" % filepath)
        
    mode = st.st_mode
    
    # Others
    if mode & stat.S_IWOTH:
        return
    
    try:
        passdb_entry = pwd.getpwnam(user_name)
    except KeyError:
        fail("no user called (%s) on the system" % user_name)
    user_id = passdb_entry.pw_uid
    group_id = passdb_entry.pw_gid
    
    owner_uid = st.st_uid
    owner_gid = st.st_gid
    
    if owner_gid == group_id:
        if mode & stat.S_IWGRP:
            return
    
    if owner_uid == user_id:
        if mode & stat.S_IWUSR:
            return
    
    fail("user (%s) has no write access on file (%s)" % (user_name, filepath))

def get_ini_config_value(file_path, section, key): # returns a value for an attribute in a file "used with configuration files"
    parser = ConfigParser.ConfigParser()
    parser.read(file_path)
    value = parser.get(section, key)
    return value

def get_apache_config_value(file_path, section, module_name, key):
    with open(file_path) as file:
        try:
            text = file.read()
            section_start = "<"+section + " "+module_name + ">"
            section_end  = "</"+ section+">"
            all_sections = re.findall(r'\</?[^\>]+\>([\s\S]+)\<//?[^\>]+\>', text, re.MULTILINE)[0]
            print "all sections : ", all_sections
            
            split_start = all_sections.index(section_start)
            split_end = all_sections.index(section_end)
            wanted_section = all_sections[split_start +1: split_end]
            section_lines = wanted_section.split('\n')
            value = ""
            for line in section_lines:
                cleaned = line.strip()
                if cleaned.startswith(key):
                    value = cleaned[len(key)+1:]
                    break
            return value
        except:
            return ""

def get_file_configvalue(filepath,key, delimeter):
    #needs to be fixed or replaced
    line=os.popen("grep ^"+key+" "+filepath).readline()
    try:
        if line.startswith("#"):
            return None
        tuple_line=line.partition(delimeter)
        return tuple_line[2].strip()
    except:
        return None

def get_keys_value(filepath, key, delimeter):
    lines = open(filepath).readlines()
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            continue
        elif line.startswith(key):
            value = line.split(delimeter)[1]
            return value
    return ""
    

def check_filemode(filepath, mode):
    """Return True if 'file' matches ('permission') which should be entered in octal.
    """

    filemode = stat.S_IMODE(os.stat(filepath).st_mode)
    return (oct(filemode) == mode)

def get_modification_datetime(filepath):
      latest_modified = os.path.getmtime(filepath)
      return latest_modified

def is_recently_modified(filepath, threshold):
    mod_datetime = get_modification_datetime(filepath)
    delta = float(time.strftime("%s", time.localtime())) - mod_datetime
    if delta < threshold:
        return True
    return False
  
def check_exists(filepath):
    return os.path.exists(filepath)

def get_source_of_symbolic_link(symbolic):
    state = os.lstat(symbolic) 
    if stat.S_ISLNK(state.st_mode): 
        dest = os.popen("ls -l %s" % symbolic).readline().strip().split()[-1]
        return dest
    else:
        fail("File is not a symbolic link")

def get_permissions(filepath):
    permissions = oct(os.stat(filepath)[ST_MODE])[-3:]
    return permissions

def get_owner(filepath):
    uid = os.stat(filepath).st_uid
    owner = getpwuid(uid).pw_name
    return owner
def all_lines_commented(filepath):
    all_lines = [line.strip() for line in open(filepath).readlines()]
    for line in all_lines:
        if line:
            if not line.startswith("#"):
                return False
    return True

def check_hidden(file):
    return file.startswith('.') or file.endswith("~")
    
def list_dir(directorypath, show_hidden=False):
    hidden_cond = (lambda _: False) if show_hidden else check_hidden
    files_list = [cont for cont in os.listdir(directorypath) if os.path.isfile(os.path.join(directorypath, cont)) if not hidden_cond(cont)]
    directory_list = [cont for cont in os.listdir(directorypath) if os.path.isdir(os.path.join(directorypath, cont)) if not hidden_cond(cont)]
    return files_list, directory_list
    
def search_all_files(path, search):
    dirs_list = [os.path.join(dirname, subdirname) for dirname, dirnames, _ in os.walk(path) for subdirname in dirnames if subdirname == search]
    files_list = [os.path.join(dirname, filename) for dirname, _, filenames in os.walk(path) for filename in filenames if filename == search]
    return files_list, dirs_list

def search_by_extension(path, extension):
    return [os.path.join(dirname,filename) for dirname, _, filesnames in os.walk(path) for filename in filesnames if filename.endswith(extension)]


def is_empty(filepath):
    return os.stat(filepath)[6]==0

def user_access(path, username):
    return True if username == get_owner(path) else False
    
def extract_correct(extractpath, extractfiles = [], extractdirs = [] ):
    files, dirs = list_dir(extractpath)
    if extractdirs:
        for dir in dirs:
            if not (dir in extractdirs):
                return False
    if extractfiles:
        for file in files:
            if not (file in extractfiles):
                return False
    return True


    