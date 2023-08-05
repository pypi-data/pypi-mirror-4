#!/home/tibi/tools/bin/python
# -*- coding: utf-8 -*-

from iso8601 import parse_date
from pprint import pprint
from utils import initialize_service, process_flags
import datetime
import sys

#CALENDAR = "Tiberiu Ichim - Fisa de pontaj"
CALENDAR = "Pontaj Zoli"
#CALENDAR = "David Ichim - timesheet"


def convert_date(s):
    year, month, day = map(int, s.split('-'))
    return datetime.date(year=year, month=month, day=day)


def main(argv):

    raport = open('raport-zoli.txt', 'w')

    process_flags(sys.argv)
    service = initialize_service()

    cals = service.calendarList().list().execute()
    #list(minAccessRole="owner")

    cal_id = None
    for item in cals['items']:
        summary = item.get('summaryOverride') or item['summary'] 
        if summary == CALENDAR:
            cal_id = item['id']
            break

    if not cal_id:
        print "Calendar not found"
        sys.exit()

    all_events = []

    token = None
    while True:
        events = service.events().list(calendarId=cal_id, 
                                        pageToken=token).execute()
        print "Got %s events" % len(events['items'])
        all_events.extend(events['items'])
        token = events.get('nextPageToken')
        if not token:
            break

    summaries = {}
    for event in all_events:
        summary = event['summary']
        if 'dateTime' in event['start']:
            date = parse_date(event['start']['dateTime'])
        else:
            date = convert_date(event['start']['date'])

        date = datetime.date(year=date.year, month=date.month, day=date.day)
        month = datetime.date(year=date.year, month=date.month, day=1)

        if not month in summaries:
            summaries[month] = {}

        if not date in summaries[month]:
            summaries[month][date] = []
        summaries[month][date].append(summary)

    #pprint(summaries)


    for month in sorted(summaries.keys()):
        days = list(sorted(summaries[month]))
        lucrate = []
        for day in days:
            lucrate.append((day,  ", ".join(summaries[month][day])))

        header = "%s luna %s (%s zile lucrate)" % (month.year, month.month, len(lucrate))
        print >> raport, header
        print >> raport, "-" * len(header)

        for day, title in lucrate:
            print >> raport, "%s-%s-%s: %s" % (day.year, day.month, day.day, title)

        print >> raport, ""


    #body = {
            #"kind":"calendar#calendar",
            #"description":"My test cal 1",
            #"selected":True,
            #"summary":"My test cal sum 1",
            #"id":"my-test-cal-1"
            #}
    #print service.calendars().insert(body=body).execute()
    #print service.calendarList().list().to_json()
    #minAccessRole='owner'

if __name__ == '__main__':
    main(sys.argv)
