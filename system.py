import os
import subprocess

def run_cmd(cmd=''):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    log = {}
    log['exitcode'] = sp.wait()
    log['stdout'] = str(sp.stdout.read(), 'utf-8')
    log['stderr'] = str(sp.stderr.read(), 'utf-8')
    result = "\033[0;32mEXITCODE: %s, CMD: %s\033[00m\n%s " % (log['exitcode'], cmd, log['stdout'] if log['exitcode'] == 0 else log['stderr'])
    print(result)
    return(log['stdout'] if log['exitcode'] == 0 else log['stderr'])

def read_file(path):
    if os.path.exists(path):
        f = open(path, 'r')
        data = f.read()
        f.close()
        return(data)
    else:
        return('File %s not exists' % path)

def write_file(path, data):
    f = open(path, 'w')
    f.write(data)
    f.close()
