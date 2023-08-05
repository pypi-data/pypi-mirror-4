#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################
# CLAM: Computational Linguistics Application Mediator
# -- CLAM Webservice --
#       by Maarten van Gompel (proycon)
#       http://proycon.github.com/clam
#
#       Centre for Language Studies
#       Radboud University Nijmegen
#
#       Induction for Linguistic Knowledge Research Group
#       Tilburg University
#       
#       Licensed under GPLv3
#
###############################################################

import sys

try:
    import clam
except:
    print >>sys.stderr, "ERROR: Unable to find CLAM. Either something went wrong during installation or you did not install CLAM globally and are in a directory from which it can not be accessed."
    sys.exit(2)

import getopt

def usage():
        print >> sys.stderr, "Syntax: clamnewproject.py system_id"
        print >> sys.stderr, "Description: This tool sets up a new CLAM project for you. Replace 'system_id' with a short ID/name for your project, for internal use only, no spaces allowed."        
        print >> sys.stderr, "Options:"
        print >> sys.stderr, "\t-d [dir]      - Directory prefix, rather than in current working directory"
        print >> sys.stderr, "\t-H [hostname] - Hostname"
        print >> sys.stderr, "\t-p [port]     - Port"
        print >> sys.stderr, "\t-u [url]      - Force URL"
        print >> sys.stderr, "\t-h            - This help message"
        
        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    sysid = sys.argv[1]
    if ' ' in sysid or '/' in sysid or "'" in sysid or '"' in sysid:
        print >>sys.stderr, "Invalid characters in system ID"
        sys.exit(2)        
    
    PORT = HOST = FORCEURL = None
    dirprefix = "."
    force = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:cH:p:u:f")
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-d':
            dirprefix = a
        elif o == '-H':
            HOST = a
        elif o == '-p':
            PORT = int(a)
        elif o == '-h':
            usage()
            sys.exit(0)
        elif o == '-u':
            FORCEURL = a
        elif o == '-f':
            force = True
        else:
            usage()
            print "ERROR: Unknown option: ", o
            sys.exit(2)


    
    clampath = clam.__path__[0]
    
    if os.path.exists(clampath + '/config/template.py') and os.path.exists(clampath + '/wrappers/template.py'):        
        print >>sys.stderr, "ERROR: Templates not found. Unable to create new project"
        sys.exit(2)
    
    dir = dirprefix + "/" +sysid
        
    if os.path.exists(dir):
        if not force:
            print >>sys.stderr, "ERROR: Directory " +dir + " already exists.. Unable to make new CLAM project. Add -f (force) if you want to continue nevertheless "
            sys.exit(2)
    else:
        print >>sys.stderr, "Making project directory " + dir
        os.mkdir(dir)
    
    if not os.path.exists(dir+ "/__init__.py"):
        f = open(dir+ "/__init__.py",'w')
        f.close()

    if not os.path.exists(dir + '/' + sysid + '.py'):
        os.copyfile(clampath + '/config/template.py', dir + '/' + sysid + '.py')
    else:
        print >>sys.stderr, "WARNING: Service configuration file " + dir + '/' + sysid + '.py already seems to exists, courageously refusing to overwrite"
        sys.exit(2)
    
    if not os.path.exists(dir + '/' + sysid + '-wrapper.py'):
        os.copyfile(clampath + '/wrappers/template.py', dir + '/' + sysid + '-wrapper.py')
    else:
        print >>sys.stderr, "WARNING: System wrapper file " + dir + '/' + sysid + '-wrapper.py already seems to exists, defiantly refusing to overwrite"
        sys.exit(2)

        

    
    
    
    
    
    
    
    
    



            
            

