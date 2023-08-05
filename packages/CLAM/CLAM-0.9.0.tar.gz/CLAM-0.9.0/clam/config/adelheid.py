#!/usr/bin/env python
#-*- coding:utf-8 -*-


###############################################################
# CLAM: Computational Linguistics Application Mediator
# -- Settings --
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
#
###############################################################

from clam.common.parameters import *
from clam.common.formats import *
from clam.common.converters import *
from clam.common.viewers import *
from clam.common.data import *
from clam.common.digestauth import pwhash
import sys

REQUIRE_VERSION = 0.5

# ======== GENERAL INFORMATION ===========

#The System ID, a short alphanumeric identifier for internal use only
SYSTEM_ID = "adelheid"

#System name, the way the system is presented to the world
SYSTEM_NAME = "Adelheid"

#An informative description for this system:
SYSTEM_DESCRIPTION = "This webservice annotates historical Dutch texts with word class tags and lemmas."

# ======== LOCATION ===========

#The root directory for CLAM, all project files, (input & output) and
#pre-installed corpora will be stored here. Set to an absolute path:
ROOT = "/home/adelheid/clam/adelheid"

#The URL of the system
HOST= 'wwwlands2.let.kun.nl'
URLPREFIX = 'adelheid'
#PORT= 8080

# ======== AUTHENTICATION & SECURITY ===========

#Users and passwords
USERS = None #no user authentication
#USERS = { 'admin': pwhash('admin', SYSTEM_ID, 'secret'), 'proycon': pwhash('proycon', SYSTEM_ID, 'secret'), 'antal': pwhash('antal', SYSTEM_ID, 'secret') , 'martin': pwhash('martin', SYSTEM_ID, 'secret') }

#ADMINS = ['admin'] #Define which of the above users are admins
#USERS = { 'username': pwhash('username', SYSTEM_ID, 'secret') } #Using pwhash and plaintext password in code is not secure!! 

#Do you want all projects to be public to all users? Otherwise projects are 
#private and only open to their owners and users explictly granted access.
PROJECTS_PUBLIC = False

#Amount of free memory required prior to starting a new process (in MB!), Free Memory + Cached (without swap!)
REQUIREMEMORY = 0 #10 * 1024

#Maximum load average at which processes are still started (first number reported by 'uptime')
MAXLOADAVG = 0 #1.0


# ======== WEB-APPLICATION STYLING =============

#Choose a style (has to be defined as a CSS file in style/ )
STYLE = 'classic'

# ======== ENABLED FORMATS ===========

#Here you can specify an extra formats module
CUSTOM_FORMATS_MODULE = None


# ======== PREINSTALLED DATA ===========


# ======== PROFILE DEFINITIONS ===========

PROFILES = [ 
    Profile(
        InputTemplate('textinput', PlainTextFormat,"Input text document",  
            StaticParameter(id='encoding',name='Encoding',description='The character encoding of the file', value='utf-8'),  
            unique=True
        ),
        InputTemplate('lexicon', PlainTextFormat,"Input lexicon",  
            StaticParameter(id='encoding',name='Encoding',description='The character encoding of the file', value='utf-8'),  
            FloatParameter(id='weight',name='Lexicon weight',description="Weight of the lexicon (base=1)", minvalue=0,maxvalue=100),
            unique=True
        ),
        OutputTemplate('ascxmloutput', PlainTextFormat,'ASC output in XML', 
            SetMetaField('encoding','utf-8'),
            unique=True
        ),
        OutputTemplate('atlxmloutput', PlainTextFormat,'ASC output in XML', 
            SetMetaField('encoding','utf-8'),
            unique=True
        ),
        OutputTemplate('tagoutput', PlainTextFormat,'tag output', 
            SetMetaField('encoding','utf-8'),
            unique=True
        )
    ),
    Profile(
        InputTemplate('textinput', PlainTextFormat,"Input text document",  
            StaticParameter(id='encoding',name='Encoding',description='The character encoding of the file', value='utf-8'),  
            unique=True
        ),
         OutputTemplate('ascxmloutput', PlainTextFormat,'ASC output in XML', 
            SetMetaField('encoding','utf-8'),
            unique=True
        ),
        OutputTemplate('atlxmloutput', PlainTextFormat,'ASC output in XML', 
            SetMetaField('encoding','utf-8'),
            unique=True
        ),
        OutputTemplate('tagoutput', PlainTextFormat,'tag output', 
            SetMetaField('encoding','utf-8'),
            unique=True
        )
    ) 
]

# ======== COMMAND ===========

#The system command. It is recommended you set this to small wrapper
#script around your actual system. Full shell syntax is supported. Using
#absolute paths is preferred. The current working directory will be
#set to the project directory.
#
#You can make use of the following special variables, 
#which will be automatically set by CLAM:
#     $INPUTDIRECTORY  - The directory where input files are uploaded.
#     $OUTPUTDIRECTORY - The directory where the system should output
#                        its output files.
#     $STATUSFILE      - Filename of the .status file where the system 
#                        should output status messages. 
#     $DATAFILE        - Filename of the clam.xml file describing the 
#                        system and chosen configuration.
#     $USERNAME        - The username of the currently logged in user
#                        (set to "anonymous" if there is none)
#     $PARAMETERS      - List of chosen parameters, using the specified flags
#
COMMAND = "/home/adelheid/clam/wrappers/adelheid.py $DATAFILE $STATUSFILE $OUTPUTDIRECTORY"

# ======== PARAMETER DEFINITIONS ===========

#The parameters are subdivided into several groups. In the form of a list of (groupname, parameters) tuples. The parameters are a list of instances from common/parameters.py
PARAMETERS =  [ 
    ('Main', [ 
#        BooleanParameter(id='distok',name='DistributeTok',description='Distribute Tokenisation?'),
        StringParameter(id='tokurl',name='Tokenisation URL',description='Give the URL of the distributed Tokenisation, if you do not want it done internally',maxlength=255),
#        BooleanParameter(id='dislex',name='DistributeLex',description='Distribute Tag Assignment?'),
        StringParameter(id='lexurl',name='Lexicon URL',description='Give the URL of the distributed Tag Assignment, if you do not want it done internally',maxlength=255)
#        BooleanParameter(id='disdis',name='DistributeDis',description='Distribute Disambiguation?'),
#        BooleanParameter(id='disall',name='DistributeAll',description='Distribute Everything?')
    ] )
]

