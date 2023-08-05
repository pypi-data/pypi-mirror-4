"""Read activity from redmine
"""

from lxml.html import etree
from lxml.html.soupparser import fromstring
from trac2google.cal import sync_to_google
from trac2google.config import TICKET_RE, get_config
import calendar
import datetime
import os
import pprint
import sys
import urllib



URL = ("%s/activity?"
       "from=%s" #date in format  2012-10-29
       "&user_id=%s"
       "&show_issues=1&show_changesets=1&show_news=1&show_documents=1&show_files=1"
       "&show_wiki_edits=1&show_messages=1&show_time_entries=1"
       )


NOW = datetime.datetime.now()


def get_tickets(trac_id, trac_url, from_date):
    work = {}
    while trac_url.endswith('/'):
        trac_url = trac_url[:-1]

    trac_date = "%s-%s-%s" % (from_date.year, from_date.month, from_date.day)

    url = URL % (trac_url, trac_date, trac_id)
    conn = urllib.urlopen(url)
    data = conn.read()
    try:
        root = fromstring(data)
    except etree.XMLSyntaxError:
        print "Could not parse response from trac"
        sys.exit(1)

    workdays = root.xpath("//div[@id='activity']/h3")
    for workday in workdays:
        print workday
        day = workday.text
        if day == "Today":
            day = NOW
        else:
            day = datetime.datetime.strptime(day, "%d/%m/%Y").date()

        if not day.month == from_date.month:
            continue

        activities = [x.text for x in workday.getnext().xpath("dt/a")]
        for title in activities:
            tickets = TICKET_RE.findall(title)
            info = work.get(day.day, [])
            info = list(set(info + [x[1:] for x in tickets]))
            work[day.day] = info

    pprint.pprint(work)

    return work


def main():

    month = None
    if len(sys.argv) == 2:
        month = int(sys.argv[1])
    else:
        month = NOW.month

    f_path         = os.path.expandvars("$HOME/.gcalendar")
    config         = get_config(f_path)
    user           = config['user']
    pwd            = config['password']
    trac_id        = config['trac_id']
    calendar_title = config['calendar']
    trac_url       = config['trac_url']

    year = NOW.year
    monthend = calendar.monthrange(year, month)[1]
    from_date = datetime.date(year, int(month), monthend)

    work = get_tickets(trac_id, trac_url, from_date)
    sync_to_google(month, work, config)

if __name__ == "__main__":
    main()

