import json
import urllib2
import os
import fileinput
import calendar
import re
from peewee import *
from datetime import datetime


db_path = os.path.abspath('./logan_blotter.db')
db = SqliteDatabase(db_path)

class Report(Model):
    incident_num = CharField(unique=True)
    date_reported = DateField()
    dispos = CharField()
    nature = CharField()
    agency = CharField(null=True)
    narrative = TextField()

    class Meta:
        order_by = ('date_reported',)
        database = db

db.connect()

data = urllib2.urlopen('http://www.loganutah.org/Police/Reports/json/calls.cfm?hours=100000')
reports = json.load(data)['DATA']
# reports = [[str(r).rstrip('\n\n') for r in report] for report in reports]

day_abrv = [ "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ]
today = datetime.today()
month_abbr = calendar.month_abbr[today.month]


reports = [[r for r in report] for report in reports]

for r in reports:

    # Narrative
    # Find a year in the string and strip away all of it
    strip_year = r"^.*\b" + str(today.year) + "(.*?\n\n|.*?\s\s|\s\b|.*?Powell\s)"
    strip_line_breaks = r"(\n|\n\n)"
    strip_trailing_spaces = r"(^\s*|\s*$)"
    narrative = re.sub(strip_year, "", r[5], 1)
    narrative = re.sub(strip_line_breaks, " ", narrative)
    narrative = re.sub(strip_trailing_spaces, "", narrative)

    # print narrative
    print r[0].rstrip()
    r = Report.create(
    incident_num  = r[0].rstrip(),
    date_reported = datetime.strptime(r[1], "%B, %d %Y %H:%M:%S"),
    dispos        = r[2].rstrip(),
    nature        = r[3].rstrip(),
    agency        = r[4],
    narrative     = narrative
    )
    # r = Report()
    # r.incident_num  = report[0].rstrip(),
    # r.date_reported = datetime.strptime(report[1], "%B, %d %Y %H:%M:%S"),
    # r.dispos        = report[2].rstrip(),
    # r.nature        = report[3].rstrip(),
    # r.agency        = report[4].rstrip(),
    # r.narrative     = narrative
    # user, created = Report.create_or_get(incident_num=r.incident_num)
    # year_pos = r[5].find(str(today.year), 15, 35)
    # if year_pos > 0:

    #     date_rmvd = r[5][year_pos+4:]
    #     #     import pdb; pdb.set_trace()
    #     line_breaks = date_rmvd.find("\n\n", 0, 25)
    #     # print date_rmvd
    #     date_rmvd = date_rmvd.replace("\n", " ")
    #     if line_breaks >= 0:
    #         # print "line_breaks FOUND"
    #         date_rmvd = date_rmvd[line_breaks+2:]
    #         print date_rmvd
    #     else:
    #         date_rmvd = date_rmvd.replace("  ", "", 1)
    #         # print date_rmvd

    # else:
    #     pass
        # print r[5]
    # if r[5].split(' ', 1)[0] in day_abrv:
    #     print r[5].split(' ', 1)[0]
    # else:
    #     print "nope"
    # import pdb; pdb.set_trace()
    # break

# print j['COLUMNS']
# print "records returned:", len(j['DATA'])
# August, 21 2015 20:24:41
# print j['DATA'][0][1]
# cols = [u'NUMBER', u'DTREPOR', u'DISPOS', u'NATURE', u'AGENCY', u'NARRATV']
# date = datetime.strptime(j['DATA'][0][1], "%B, %d %Y %H:%M:%S")

# for report in reports['DATA']:

#     r = Report.create(
#         incident_num  = report[0],
#         date_reported = datetime.strptime(report[1], "%B, %d %Y %H:%M:%S"),
#         dispos        = report[2].rstrip(),
#         nature        = report[3].rstrip(),
#         agency        = report[4],
#         narrative     = report[5]
#         )

# rep = Report.create(incident_num="abcd", date_reported=datetime.today(), 
#     dispos="blah", nature="blahaa", agency="YES", narrative="STUFF HAPPENED")
# import pdb; pdb.set_trace()
print Report.select().count()
# for r in Report.select():
#     r.delete_instance()
