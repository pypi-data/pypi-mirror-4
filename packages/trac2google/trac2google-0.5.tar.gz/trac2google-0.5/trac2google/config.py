import os
import sys
import re

TICKET_RE = re.compile(r"\#\d+")

def get_config(f_path):
    CONFIG = {}
    if os.access(f_path, os.R_OK):
        for ln in open(f_path).readlines():
            if not ln[0] in ('#',';'):
                key,val=ln.strip().split('=',1)
                CONFIG[key.lower()]=val

    for mandatory in ['user','password', 'trac_id', 'calendar']:
        if mandatory not in CONFIG.keys():
            open(f_path,'w').write(
                '#Uncomment fields before use and type in correct '
                'credentials.\n#USER=example@gmail.com'
                '\n#PASSWORD=placeholder\nTRAC_ID=some_trac_id\n'
                'CALENDAR=My Timesheet\nTRAC_URL=http://sometrac.org/')
            print 'Please point ~/.gcalendar to valid credentials'
            sys.exit(1)

    return CONFIG

