import os
import subprocess
import time


null = open('/dev/null', 'wb')

try:
    os.remove('log/zc')
except OSError:

    pass
cmd = 'python browse_resolve_query.py > log/zc'
zc = subprocess.Popen(cmd, shell=True)
time.sleep(5)
zc.kill()

log = open('log/zc', 'r').read()
if log == "":
    print "err"
else:
    print log + "----"
