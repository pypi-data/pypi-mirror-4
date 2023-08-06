import results
from jenkinsapi import api
import sys, optparse

def fetch_test_results():
  p = optparse.OptionParser()
  p.add_option('--jenkinsurl', '-u')
  p.add_option('--job', '-j')
  options, arguments = p.parse_args()

  if not options.jenkinsurl or not options.job:
    print "Must specify both the Jenkins URL and Job Name"
    sys.exit(1)

  jenkins = api.Jenkins(options.jenkinsurl)
  job = jenkins.get_job(options.job)

  result_sets = results.get_result_sets(job)
  counts = results.get_counts(result_sets, csv=True)

  num = 20
  print "Top %d tests by failures" % num
  print results.top_fails(counts, n=num, csv=True).to_string()
