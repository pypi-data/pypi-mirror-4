def __bootstrap():
    import subprocess
    import sys
    import os
    import imp
    import pkgutil
    from subprocess import Popen, PIPE, CalledProcessError
    import logging
    __logger = logging.getLogger("TG SDK")
    
    def __check_output(*popenargs, **kwargs):
        r"""Run command with arguments and return its output as a byte string.
        If the exit code was non-zero it raises a CalledProcessError.  The
        CalledProcessError object will have the return code in the returncode
        attribute and output in the output attribute.
    
        The arguments are the same as for the Popen constructor.  Example:
     
        >>> check_output(["ls", "-l", "/dev/null"])
        'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'
    
        The stdout argument is not allowed as it is used internally.
        To capture standard error in the result, use stderr=STDOUT.
    
        >>> check_output(["/bin/sh", "-c",
        ...               "ls -l non_existent_file ; exit 0"],
        ...              stderr=STDOUT)
        'ls: non_existent_file: No such file or directory\n'
        """
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = Popen(stdout=PIPE, *popenargs, **kwargs)
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output
    
    def __magical_import(base_package):
        base_path = os.path.dirname(os.path.realpath(base_package.__file__))
        __logger.debug("Loading Modules/Packages from %s" % os.path.join(base_path, sys.platform))
        for _, mod_name, is_pkg in pkgutil.iter_modules([base_path, os.path.join(base_path, sys.platform)]):
            __logger.debug("Loading %s" % mod_name)
            mod = imp.load_module(mod_name, *imp.find_module(mod_name, [base_path, os.path.join(base_path, sys.platform)]))
            setattr(base_package, mod.__name__, mod)
            if not is_pkg:
                __logger.debug("Module %s is now Loaded" % mod_name)
            else:
                __logger.debug("Loading Package %s" % mod_name)
                __magical_import(mod)
                
    # a hack to add check_output to Python < 2.6
    if 'check_output' not in subprocess.__all__:
        subprocess.check_output = __check_output
    current_module = sys.modules[__name__]
    __magical_import(current_module)
    
__bootstrap()