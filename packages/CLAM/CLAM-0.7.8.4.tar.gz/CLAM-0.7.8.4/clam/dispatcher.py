#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import datetime

settingsmodule = sys.argv[1]
projectdir = sys.argv[2]
if projectdir[-1] != '/':
    projectdir += '/'

cmd = " ".join(sys.argv[3:])

print >>sys.stderr, "[CLAM Dispatcher] Started (" + datetime.datetime.strftime('%Y-%m-%d %H:%M:%S') + ")"

if not cmd:
    print >>sys.stderr, "[CLAM Dispatcher] FATAL ERROR: No command specified!"
    sys.exit(1)

exec "import " + settingsmodule + " as settings"
settingkeys = dir(settings)



process = subprocess.Popen(cmd,cwd=projectdir, shell=True)				



if process:
    pid = process.pid
    printlog("Started with pid " + str(pid) )
    f = open(projectdir + '.pid','w')
    f.write(str(pid))
    f.close()
else:
    sys.exit(1)
    
print >>sys.stderr, "[CLAM Dispatcher] Finished (" + datetime.datetime.strftime('%Y-%m-%d %H:%M:%S') + ")"
    

