from subprocess import PIPE, STDOUT,  Popen

def powershell(command):
    args = [r'C:\WINDOWS\system32\WindowsPowerShell\v1.0\powershell.exe', '-Command', command]
    p = Popen(args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    output,_ = p.communicate()
    return output

def check_service(service_name):
    command = "Get-service -name %s*" % service_name
    output = powershell(command)
    if output.find('Running  IIS') < 0:
        return "IIS Not Running"
    #return "IISAdmin is running"
    process_name = "inetinfo"
    command = "Get-process -name %s" % process_name
    output = powershell(command)
    if output.find("inetinfo") > 0:
        process_id = output.split(" inetinfo")[0].split()[-1:][0]
        command = 'iex "netstat -ano | findstr %s"' % process_id
        output = powershell(command)
        if output.find(":80") > 0:
            return "IIS is Running on port 80"