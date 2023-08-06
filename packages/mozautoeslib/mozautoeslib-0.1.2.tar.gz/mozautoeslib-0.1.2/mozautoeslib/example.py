from mozautoeslib import ESLib
try:
  import json
except:
  import simplejson as json
import re
import datetime

if __name__ == '__main__':
  # example: all instances of a specific bug during a specific date range
  eslib = ESLib('elasticsearch1.metrics.scl3.mozilla.com:9200', 'bugs', 'bug_info')
  result = eslib.query({'bug': '614643',                                # must include bug '614643'
                        'tree': ('mozilla-central', 'tracemonkey'),     # must include tree 'mozilla-central' OR 'tracemonkey'
                        'date': ['2011-01-25', '2011-01-26']})          # must have date in range from '2010-12-21' to '2011-01-01'
  print json.dumps(result, indent=2)
  print "%d hits" % len(result)

  # example: top bugs during a specific date range
  result = eslib.frequency(include = {
                                        'tree': 'mozilla-central',
                                        'date': ['2011-01-29', '2011-01-29']
                                     },
                           frequency_fields = ["bug"]
                          )
  print json.dumps(result, indent=2)

  date1 = datetime.datetime(2011, 1, 30)
  date2 = datetime.datetime(2011, 1, 30)
  # example: list of unique testruns on a specific date or date range
  eslib = ESLib('elasticsearch1.metrics.scl3.mozilla.com:9200', 'logs', 'builds')
  result = eslib.frequency(include = {
                                        'repo': 'mozilla-central',
                                        'date': [date1, date2],
                                     },
                           frequency_fields = ["buildid"]
                          )
  buildids = result['buildid']['terms']
  print json.dumps(result, indent=2)
  print "%d unique buildid's" % len(buildids)

  termre = re.compile('([0-9][0-9][0-9][0-9])([0-9][0-9])([0-9][0-9])[0-9]+')
  testruns = {}
  count = 0
  for build in buildids:
      matches = termre.search(build["term"])
      if not matches:
          continue
      year = matches.group(1)
      month = matches.group(2)
      day = matches.group(3)
      date = "%s-%s-%s" % (year, month, day)
      try:
          x = testruns[date]
      except:
          testruns[date] = []
      testruns[date].append(build)
      count += 1
  print count
  print testruns

  # querying from multiple doc types
  eslib = ESLib('elasticsearch1.metrics.scl3.mozilla.com:9200', 'logs', ['testruns', 'testfailures'])
  result = eslib.query({'repo': 'mozilla-central',
                        'machine': 'talos-r3-leopard-046',
                        'starttime': '1297070365'})
  print json.dumps(result, indent=2)

