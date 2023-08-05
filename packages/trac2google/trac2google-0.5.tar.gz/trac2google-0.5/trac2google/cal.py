#!/home/tibi/tools/bin/python

from gdata.calendar import service, CalendarEventEntry, When
from lxml import etree
import atom
import calendar
import datetime
import gdata
import time
import re
import sys
import urllib
import os


URL = ("%s/timeline?changeset=on&ticket=on&wiki=on&max=500&format=rss&"
       "from=%s" #date in format "02%2F05%2F12"
       "&authors=%s"
       "&daysback=%s" )


ticket_re = re.compile(r"\#\d+")
now = datetime.datetime.now()

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


def get_tickets(trac_id, trac_url, month):
    work = {}
    while trac_url.endswith('/'):
        trac_url = trac_url[:-1]

    #compute year. If month is greater then current month
    #assume last year
    this_year = now.year
    this_month = now.month
    if not month:
        month = this_month
    month = int(month)
    if month > this_month:
        this_year = this_year - 1

    daysback = calendar.monthrange(this_year,month)[1]
    start_date = "%2F".join(map(str, (daysback, month, this_year - 2000)))

    url = URL % (trac_url, start_date, trac_id, daysback)
    conn = urllib.urlopen(url)
    data = conn.read()
    try:
        root = etree.fromstring(data)
    except etree.XMLSyntaxError:
        print "Could not parse response from trac"
        sys.exit(1)

    entries = root.xpath('//item')

    for entry in entries:
        title = entry.find('title').text
        tickets = ticket_re.findall(title)
        if tickets:
            tickets = map(lambda s:s.replace("#", ""), tickets)
            pubdate = entry.find('pubDate').text.replace("#", "")
            date = datetime.datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            #date = iso8601.parse_date(pubdate)
            day = date.day

            if date.month == month:
                info = work.get(day, [])
                info = list(set(info + tickets))
                work[day] = info

    return work


def sync_to_google(month, work, config):
    user           = config['user']
    pwd            = config['password']
    trac_id        = config['trac_id']
    calendar_title = config['calendar']
    trac_url       = config['trac_url']

    #work = get_tickets(trac_id, trac_url, month)

    #feed = "/calendar/feeds/default/private/full"

    gc = service.CalendarService()
    gc.email = user
    gc.password = pwd
    gc.source = 'sgtdev-pythonCalendarHelper-0.1'
    gc.ProgrammaticLogin()

    try:
        calendar_id = [o.GetSelfLink().href for o in gc.GetOwnCalendarsFeed().entry
                if o.title.text == calendar_title][0].split('/')[-1]
    except IndexError:
        print "Could not find calendar named %s" % calendar_title
        sys.exit(1)

    uri = "/calendar/feeds/%s/private/full" % calendar_id
    cal = gc.GetCalendarEventFeed(uri)
    batch_url = cal.GetBatchLink().href
    entries = cal.entry
    old = {}

    for e in entries:
        year, m, day = map(int, e.when[0].start_time.split('-'))
        d = datetime.date(year=year, month=m, day=day)
        old[d] = e.title.text.replace("#", "").split(" ")

    modified = False
    for day, tickets in work.items():
        start_date = datetime.date(now.year, month, day)
        if start_date in old:   #don't add tickets to events already filled
            continue

        modified = True
        title = " ".join(map(lambda s:"#"+s, tickets))
        d = "%s-%02d-%02d" % (start_date.year, start_date.month, start_date.day)

        when = [When(start_time=d, end_time=d)]
        event = CalendarEventEntry()
        event.title = atom.Title(text=title)
        event.when = when

        print "Inserting ", title, d
        cal.AddInsert(entry=event)   #, insert_uri=uri

    if not modified:
        return

    print "Saving"
    trying = True
    attempts = 0
    sleep_secs = 1
    gsessionid = ''
    calendar_service = gc   #gdata.calendar.service.CalendarService()
    request_feed = cal
    while trying:
        trying = False
        attempts += 1
        try:
            response_feed = calendar_service.ExecuteBatch(request_feed, 
                                batch_url + gsessionid)
                                #gdata.calendar.service.DEFAULT_BATCH_URL
        except gdata.service.RequestError as inst:
            thing = inst[0] 
            if thing['status'] == 302 and attempts < 8:
                trying = True
                gsessionid=thing['body'][ thing['body'].find('?') : thing['body'].find('">here</A>')]
                print 'Received redirect - retrying in', sleep_secs, 'seconds with', gsessionid
                time.sleep(sleep_secs)
                sleep_secs *= 2
            else:
                print 'too many RequestErrors, giving up'
    print "done"
    return

def read_tickets_for_month():
    f_path         = os.path.expandvars("$HOME/.gcalendar")
    config         = get_config(f_path)
    user           = config['user']
    pwd            = config['password']
    trac_id        = config['trac_id']
    calendar_title = config['calendar']
    trac_url       = config['trac_url']

    #work = get_tickets(trac_id, trac_url, month)

    #feed = "/calendar/feeds/default/private/full"

    gc = service.CalendarService()
    gc.email = user
    gc.password = pwd
    gc.source = 'sgtdev-pythonCalendarHelper-0.1'
    gc.ProgrammaticLogin()

    try:
        calendar_id = [o.GetSelfLink().href for o in gc.GetOwnCalendarsFeed().entry
                if o.title.text == calendar_title][0].split('/')[-1]
    except IndexError:
        print "Could not find calendar named %s" % calendar_title
        sys.exit(1)

    uri = "/calendar/feeds/%s/private/full" % calendar_id
    cal = gc.GetCalendarEventFeed(uri)
    #cal.AddQuery("start_date=2012-02-01 end_date=2012-02-29")
    entries = cal.entry
    old = {}

    for e in entries:
        year, m, day = map(int, e.when[0].start_time.split('-'))
        d = datetime.date(year=year, month=m, day=day)
        old[d] = e.title.text.replace("#", "").split(" ")

    for k, v in old.items():
        print k, v

def main():
    read_tickets_for_month()
    return
    month = None
    if len(sys.argv) == 2:
        month = int(sys.argv[1])
    else:
        month = now.month
    sync_to_google(month)

if __name__ == "__main__":
    main()


#import icalendar
#if len(sys.argv) == 2:
    #path = sys.argv[1]
    #work = get_tickets()
    #make_ical(path, work)   #TODO: needs rework, api changed in this module
#def make_ical(path, work):
    #cal = icalendar.Calendar()
    #cal['prodid'] = "-//Timesheet importer//www.google.com//"
    #cal['version'] = '2.0'
    #for day, tickets in work.items():
        #event = icalendar.Event()
        #event.add('summary', " ".join(tickets))
        #event.add('dtstart', datetime.date(now.year, now.month, day))
        #event.add('dtend', datetime.date(now.year, now.month, day))
        #event.add('dtstamp', now)
        #event['uid'] = "".join(map(str, now.timetuple())) + "/timesheet"
        #cal.add_component(event)

    #f = open(path, 'wb') 
    #f.write(cal.to_ical())

