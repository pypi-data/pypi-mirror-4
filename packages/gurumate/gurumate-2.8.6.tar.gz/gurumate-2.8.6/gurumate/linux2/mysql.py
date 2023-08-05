import sys
import hashlib
import gurumate
import MySQLdb
class connection_mysql:
    def __init__(self, user, passwd, host):
        self.user = user
        self.passwd = passwd
        self.host = 'localhost'
    def __enter__(self):
        self.my_connection = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd)
        self.cursor = self.my_connection.cursor()
        return (self.cursor, self.my_connection)
        
    def __exit__(self, type, value, traceback):
        if self.my_connection: 
            self.my_connection.close()

def mysql_con(user, passwd, roothost='localhost'):
    try:
        my_connection = MySQLdb.connect(host=roothost, user=user, passwd=passwd)
        return True
    except MySQLdb.Error, e:
        #return "Error %d: %s" % (e.args[0], e.args[1])
        return False
        

##########Database###############
def database(user, passwd, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("show databases")
        return [db.strip("'") for db in str(cursor.fetchall()).strip('((').strip(',))').split(",), (")]
                
def database_exists(user, passwd, dbname, roothost='localhost'):
    return dbname in database(user, passwd, roothost)

def create_database(user, passwd, dbname, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("create database %s" % dbname)
        return True
        
def drop_database(user, passwd, dbname, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("drop database %s" % dbname)
        return True
        
###########Tables##############
def show_tables(user, passwd, dbname, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("use %s" % dbname)
        cursor.execute("show tables")
        return [tb.strip("'") for tb in str(cursor.fetchall()).strip('((').strip(',))').split(",), (")]

def table_exists(user, passwd, dbname, tbname, roothost='localhost'):
    return tbname in show_tables(user, passwd, dbname, roothost)

def create_table(user, passwd, dbname, tbname, columns, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("use %s" % dbname)
        #columns(firstname VARCHAR(20), middleinitial VARCHAR(3), lastname VARCHAR(35) ,officeid VARCHAR(10))
        cursor.execute("CREATE TABLE %s" % tbname + ' ' + columns)
        return True
        
def drop_table(user, passwd, dbname, tbname, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("use %s" % dbname)
        cursor.execute("DROP TABLE %s" % tbname)
        return True
        
##############User & Password###############

def users(user, passwd, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("select User from mysql.user;")
        return [username.strip("'") for username in str(cursor.fetchall()).strip('((').strip(',))').split(",), (")]
        
def user_exists(user, passwd, username, roothost='localhost'):
      return username in users(user, passwd, roothost)

def users_password(user, passwd, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("select User, Password from mysql.user;")
        return dict((username, passwd) for username, passwd in cursor.fetchall())
        
def authenticate(user, passwd, username, userpass, roothost='localhost'):
    current_passwd = users_password(user, passwd, roothost)[username]
    hash_userpass = "*" + (hashlib.sha1(hashlib.sha1(userpass).digest()).hexdigest()).upper()
    return hash_userpass == current_passwd

def no_passwd_set(user, passwd, username, roothost='localhost'):
    current_passwd = users_password(user, passwd, roothost)[username]
    return True if current_passwd == '' else False

def set_new_password_for_user(user, passwd, username, newpasswd, userhost='localhost', roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("SET PASSWORD FOR '%s'@'%s' = PASSWORD('%s');" % (username, userhost, newpasswd))
        return True
        
def add_new_user(user, passwd, newusername, newpasswd, userhost ='localhost', roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("CREATE USER '%s'@'%s' IDENTIFIED BY '%s' ;" %(newusername, userhost, newpasswd))
        return True

def drop_user(user, passwd, newusername, userhost ='localhost', roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("DROP USER '%s'@'%s' ;" %(newusername, userhost))
        return True

def users_host(user, passwd, roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("select User, Host from mysql.user;")
        return dict((username, host) for username, host in cursor.fetchall())
    
def host(user, passwd, username, reqhost, roothost='localhost'):
    return reqhost == users_host(user, passwd, roothost)[username]

def show_grant(user, passwd, username, userhost='localhost', roothost='localhost'):
    with connection_mysql(user, passwd, roothost) as (cursor, _):
        cursor.execute("SHOW GRANTS FOR '%s'@'%s';" % (username, userhost))
        return [grant.strip('"') for grant in str(cursor.fetchall()).strip('((').strip(',))').split(",), (")]
    
def grant_all_privileges(user, passwd, username, dbname, userhost='localhost', roothost='localhost'):   
    grants = show_grant(user, passwd, username, userhost, roothost)
    if len(grants) > 1:
        return True if "`"+dbname+"`.*" in grants[1] else False 
    return False
        

def create_user_correctly(user, passwd, username, userpass, roothost='localhost'):
    if not user_exists(user, passwd, username, roothost):
        gurumate.base.fail("The user <strong>%s</strong> is not yet created." % username)
    if no_passwd_set(user, passwd, username, roothost): 
        gurumate.base.fail("No password is set yet to the user <strong>%s</strong>." % username)    
    if not authenticate(user, passwd, username, userpass, roothost) :
        gurumate.base.fail("The password set to the user <strong>%s</strong> is not correct. The correct password should be <strong>%s</strong>." % (username, userpass))

#######MySQL states #############
def stop_mysql():
    gurumate.base.run_command("sudo /etc/init.d/mysql stop")

def start_mysql():
    gurumate.base.run_command("sudo /etc/init.d/mysql start")

def start_mysql_wopass():
    gurumate.base.run_command("sudo mysqld_safe --skip-grant-tables &")

def reset_root_passwd(newpass):
    stop_mysql()
    start_mysql_wopass()
    gurumate.base.run_command('sudo mysql -u root -e "use mysql;update user set password=PASSWORD(\'%s\') where User=\'root\';flush privileges;"'%(newpass))
    stop_mysql()
    start_mysql()
    return mysql_con('root', newpasswd)
    
