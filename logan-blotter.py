import json
import urllib2
import sys
import calendar
import re
import requests
from peewee import *
from datetime import datetime
from notifications import IFTTT

db_path = sys.path[0]+'/logan_blotter.db'
db = SqliteDatabase(db_path)

class Report(Model):
    incident_num = CharField(unique=True)
    date_reported = DateTimeField()
    dispos = CharField()
    nature = CharField()
    agency = CharField(null=True)
    narrative = TextField()

    class Meta:
        order_by = ('date_reported',)
        database = db

def delete_all_records():
    for r in Report.select():
        r.delete_instance()

def send_notification(value1, value2, value3):
    payload = { 'value1' : value1, 'value2' : value2, 'value3' : value3 }
    requests.post("https://maker.ifttt.com/trigger/"+IFTTT.EVENT+"/with/key/"+IFTTT.KEY, data=payload)

db.connect()

data = urllib2.urlopen('http://www.loganutah.org/Police/Reports/json/calls.cfm?hours=12')
reports = json.load(data)['DATA']

day_abrv = [ "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]
today = datetime.today()
month_abbr = calendar.month_abbr[today.month]

reports = [[r for r in report] for report in reports]

count_before = Report.select().count()

for r in reports:

    # The narrative field requires a lot of clean-up with regex
    # First we find a year in the string and strip away all of it
    # We also remove trailing whitespace and extra carriage returns
    strip_year = r"^.*\b" + str(today.year) + "(.*?\n\n|.*?\s\s|\s\b|.*?Powell\s)"
    strip_line_breaks = r"(\n|\n\n)"
    strip_trailing_spaces = r"(^\s*|\s*$)"
    narrative = re.sub(strip_year, "", r[5], 1)
    narrative = re.sub(strip_line_breaks, " ", narrative)
    narrative = re.sub(strip_trailing_spaces, "", narrative)

    # get_or_create() allows us to insert only unique records
    entry, created = Report.get_or_create(
        incident_num=r[0].rstrip(),
        defaults={
            'date_reported': datetime.strptime(r[1], "%B, %d %Y %H:%M:%S"),
            'dispos' : r[2].rstrip(),
            'nature' : r[3].rstrip(),
            'agency' : r[4],
            'narrative' : narrative } 
        )

print "Update successful"
added = Report.select().count() - count_before
print added, "records inserted"
# send_notification(added, "", "")
