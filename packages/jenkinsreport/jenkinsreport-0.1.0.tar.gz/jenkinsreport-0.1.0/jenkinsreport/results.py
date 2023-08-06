from pandas import Series, DataFrame
import pandas as pd
from jenkinsapi import api
from jenkinsapi.exceptions import NoResults
from jenkinsapi.constants import STATUS_PASSED, RESULTSTATUS_FAILED
from jenkinsapi.constants import STATUS_FIXED, STATUS_REGRESSION
import datetime, logging

log = logging.getLogger(__name__)

# The latest release of jenkinsapi does not
# have RESULTSTATUS_SKIPPED in constants.
RESULTSTATUS_SKIPPED = "SKIPPED"

def get_test_status(status):
  """
  Jenkins can report test results as FIXED or
  REGRESSION, but for simplicity, we just want
  to classify them as PASSED or FAILED.
  """
  if status == STATUS_FIXED:
    return STATUS_PASSED
  elif status == STATUS_REGRESSION:
    return RESULTSTATUS_FAILED
  else:
    return status

def get_result_sets(job):
  """
  Collect the result sets from the builds of a job.
  Return a list of tuples of (date, ResultSet).
  """
  result_sets = []
  buildIds = job.get_build_ids()
  for i in buildIds:
    build = job.get_build(i)
    if build.has_resultset():
      timestamp = build.get_timestamp()
      print timestamp
      date = datetime.datetime.fromtimestamp(int(timestamp))
      date = date.strftime('%Y-%m-%d %H:%M:%S')
      try:
        result_sets.append((date, build.get_resultset()))
      except Exception, err:
        print "Unexpected error: %s" % str(err)
    else:
      print "Build %d has no result set" % i
  return result_sets

def collect_test_statuses(result_sets, csv=False,
                          output_file="test_counts.csv"):
  """
  Collect the test result statuses and return a DataFrame
  indexed by date. The columns are the test names and the
  cell values are the result status.
  """
  test_statuses = {}
  for (date, rs) in result_sets:
    test_statuses.setdefault(date, {})
    for k, v in rs.iteritems():
      test_statuses[date][k] = get_test_status(v.status)
  return DataFrame.from_dict(counts, orient='index')

  # Optionally dump the data to csv file
  #if csv:
  #  counts.to_csv(output_file, index_label="TESTNAME")
  #return counts

# Returns a DataFrame of the top n failed tests, indexed by test
# name. Expects a DataFrame indexed by test name.
def top_fails(counts, n=10, csv=False,
              output_file="top_fails.csv"):
  fail_counts = DataFrame(counts[RESULTSTATUS_FAILED])
  fail_counts = fail_counts.sort(columns=[RESULTSTATUS_FAILED],
                                 ascending=False)
  top_failures = fail_counts[0:n]
  if csv:
    top_failures.to_csv(output_file, index_label="TESTNAME")
  return top_failures

def count_test_statuses(test_statuses):
  """
  This method constructs a table where the columns are test
  names, the rows are the test status (FAILED, PASSED, SKIPPED),
  and the cell values are the number of occurrences.
  """
  table = test_statuses.apply(lambda x: x.value_counts())
  table = table.fillna(0)
  return table

def latest_results_days_ago(test_statuses, days_ago):
  """
  This method filters out the test statuses (DataFrame indexed
  by date) that are older than days_ago.
  """
  now = datetime.datetime.now()
  days_ago = now - datetime.timedelta(days_ago)
  days_ago = a_week_ago.strftime('%Y-%m-%d %H:%M:%S')
  return test_statuses[test_statuses.index.map(
    lambda date : date >= a_week_ago)]

def latest_week_results(test_statuses):
  return latest_results_days_ago(test_statuses, 7)
