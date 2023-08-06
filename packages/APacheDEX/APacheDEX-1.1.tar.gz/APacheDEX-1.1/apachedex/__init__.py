#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from cgi import escape
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from functools import partial
from operator import itemgetter
from urllib import splittype, splithost
import argparse
import gzip
import itertools
import json
import math
import os
import platform
import re
import sys
import time
try:
  import pkg_resources
except ImportError:
  # By default, assume resources are next to __file__
  abs_file_container = os.path.abspath(os.path.dirname(__file__))
  def getResource(name):
    return open(os.path.join(abs_file_container, name)).read()
else:
  abs_file_container = None
  def getResource(name):
    return pkg_resources.resource_string(__name__, name)

MONTH_VALUE_DICT = dict((y, x) for (x, y) in enumerate(('Jan', 'Feb', 'Mar',
  'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'), 1))

US_PER_S = 10 ** 6

N_SLOWEST = 20
N_ERROR_URL = 10
N_REFERRER_PER_ERROR_URL = 5
ITEMGETTER0 = itemgetter(0)
ITEMGETTER1 = itemgetter(1)
APDEX_TOLERATING_COEF = 4

def statusIsError(status):
  return status[0] > '3'

def getClassForDuration(duration, threshold):
  if duration <= threshold:
    return ''
  if duration <= threshold * APDEX_TOLERATING_COEF:
    return 'warning'
  return 'problem'

def getClassForStatusHit(hit, status):
  if hit and statusIsError(status):
    return 'problem'
  return ''

def getApdexStyle(apdex):
  return 'color: #%s; background-color: #%s' % (
    (apdex < .5 and 'f' or '0') * 3,
    ('%x' % (apdex * 0xf)) * 3,
  )

def getApdexStatsAsHtml(data, threshold):
  apdex = data.getApdex()
  average = data.getAverage()
  maximum = data.getMax()
  hit = data.hit
  if hit:
    extra_class = ''
    apdex_style = getApdexStyle(apdex)
  else:
    extra_class = 'no_hit'
    apdex_style = ''
  return '<td style="%(apdex_style)s" class="%(extra_class)s">%(apdex)i%%' \
    '</td><td class="%(extra_class)s">%(hit)s</td>' \
    '<td class="%(average_class)s %(extra_class)s">%(average).2f</td>' \
    '<td class="%(max_class)s %(extra_class)s">%(max).2f</td>' % {
    'extra_class': extra_class,
    'apdex_style': apdex_style,
    'apdex': apdex * 100,
    'hit': hit,
    'average_class': getClassForDuration(average, threshold),
    'average': average,
    'max_class': getClassForDuration(maximum, threshold),
    'max': maximum,
  }

APDEX_TABLE_HEADERS = ''.join('<th>' + x + '</th>' for x in (
  'apdex', 'hits', 'avg (s)', 'max (s)'))

class APDEXStats(object):
  def __init__(self, threshold, getDuration):
    threshold *= US_PER_S
    self.threshold = threshold
    self.threshold4 = threshold * APDEX_TOLERATING_COEF
    self.apdex_1 = 0
    self.apdex_4 = 0
    self.hit = 0
    self.duration_total = 0
    self.duration_max = 0
    self.getDuration = getDuration

  def accumulate(self, match):
    duration = self.getDuration(match)
    self.duration_total += duration
    self.duration_max = max(self.duration_max, duration)
    if not statusIsError(match.group('status')):
      if duration <= self.threshold:
        self.apdex_1 += 1
      elif duration <= self.threshold4:
        self.apdex_4 += 1
    self.hit += 1

  def accumulateFrom(self, other):
    for attribute in ('apdex_1', 'apdex_4', 'hit', 'duration_total'):
      setattr(self, attribute,
        getattr(self, attribute) + getattr(other, attribute))
    self.duration_max = max(self.duration_max, other.duration_max)

  def getApdex(self):
    if self.hit:
      return (self.apdex_1 + self.apdex_4 * .5) / self.hit
    return 1

  def getAverage(self):
    if self.hit:
      return float(self.duration_total) / (US_PER_S * self.hit)
    return 0

  def getMax(self):
    return float(self.duration_max) / US_PER_S

class GenericSiteStats(object):
  def __init__(self, threshold, getDuration, prefix=1, error_detail=False):
    self.threshold = threshold
    self.prefix = prefix
    self.error_detail = error_detail
    self.getDuration = getDuration
    self.status = defaultdict(partial(defaultdict, int))
    if error_detail:
      self.error_url_count = defaultdict(partial(defaultdict, list))
    self.url_apdex = defaultdict(partial(APDEXStats, threshold, getDuration))
    self.apdex = defaultdict(partial(APDEXStats, threshold, getDuration))

  def accumulate(self, match, url_match, date):
    self.apdex[date].accumulate(match)
    duration = self.getDuration(match)
    if url_match is None:
      url = match.group('request')
    else:
      url = url_match.group('url')
    # XXX: can eat memory if there are many different urls
    self.url_apdex[url.split('?', 1)[0]].accumulate(match)
    status = match.group('status')
    self.status[status][date] += 1
    if self.error_detail and statusIsError(status):
      # XXX: can eat memory if there are many errors on many different urls
      self.error_url_count[status][url].append(match.group('referer'))

  def getApdexData(self):
    apdex = APDEXStats(self.threshold, None)
    for data in self.apdex.itervalues():
      apdex.accumulateFrom(data)
    return [
      (date, apdex.getApdex() * 100, apdex.hit) for date, apdex
      in sorted(self.apdex.iteritems(), key=ITEMGETTER0)]

  def asHTML(self, stat_filter=lambda x: x):
    result = []
    append = result.append
    apdex = APDEXStats(self.threshold, None)
    for data in self.apdex.itervalues():
      apdex.accumulateFrom(data)
    append('<h2>Overall</h2><table class="stats"><tr>')
    append(APDEX_TABLE_HEADERS)
    append('</tr><tr>')
    append(getApdexStatsAsHtml(apdex, self.threshold))
    append('</tr></table><h2>Hottest pages</h2><table class="stats"><tr>')
    append(APDEX_TABLE_HEADERS)
    append('<th>url</th></tr>')
    for url, data in sorted(self.url_apdex.iteritems(), key=lambda x: x[1].getAverage() * x[1].hit,
        reverse=True)[:N_SLOWEST]:
      append('<tr>')
      append(getApdexStatsAsHtml(data, self.threshold))
      append('<td class="text">%s</td></tr>' % escape(url))
    append('</table>')
    column_set = set()
    filtered_status = defaultdict(partial(defaultdict, int))
    for status, date_dict in self.status.iteritems():
      filtered_date_dict = filtered_status[status]
      for date, value in date_dict.iteritems():
        filtered_date_dict[stat_filter(date)] += value
      column_set.update(filtered_date_dict)
    column_list = sorted(column_set)
    append('<h2>Hits per status code</h2><table class="stats"><tr>'
      '<th>status</th><th>overall</th>')
    for date in column_list:
      append('<th>%s</th>' % date)
    append('</tr>')
    def hitTd(hit, status):
      return '<td class="%s">%s</td>' % (getClassForStatusHit(hit, status), hit)
    has_errors = False
    for status, data_dict in sorted(filtered_status.iteritems(),
        key=ITEMGETTER0):
      has_errors |= statusIsError(status)
      append('<tr><th>%s</th>' % status)
      append(hitTd(sum(data_dict.itervalues()), status))
      for date in column_list:
        append(hitTd(data_dict[date], status))
      append('</tr>')
    append('</table>')
    if self.error_detail and has_errors:
      def getHitForUrl(referer_counter):
        return sum(referer_counter.itervalues())
      filtered_status_url = defaultdict(partial(defaultdict, dict))
      for status, url_dict in self.error_url_count.iteritems():
        filtered_status_url[status] = sorted(
          ((key, Counter(value)) for key, value in url_dict.iteritems()),
          key=lambda x: getHitForUrl(x[1]), reverse=True)[:N_ERROR_URL]
      append('<h3>Error detail</h3><table class="stats"><tr><th>status</th>'
        '<th>hits</th><th>url</th><th>referers</th></tr>')
      for status, url_list in sorted(filtered_status_url.iteritems(),
          key=ITEMGETTER0):
        append('<tr><th rowspan="%s">%s</th>' % (len(url_list), status))
        first_url = True
        for url, referer_counter in url_list:
          if first_url:
            first_url = False
          else:
            append('<tr>')
          append('<td>%s</td><td class="text">%s</td>'
            '<td class="text">%s</td>' % (
            getHitForUrl(referer_counter),
            escape(url),
            '<br/>'.join('%i: %s' % (hit, escape(referer)) for referer, hit in sorted(
              referer_counter.iteritems(), key=ITEMGETTER1, reverse=True
            )[:N_REFERRER_PER_ERROR_URL]),
          ))
          append('</tr>')
      append('</table>')
    return '\n'.join(result)

class ERP5SiteStats(GenericSiteStats):
  """
  Heuristic used:
  - ignore any GET parameter
  - If the first in-site url chunk ends with "_module", count line as
    belonging to a module
  - If a line belongs to a module and has at least 2 slashes after module,
    count line as belonging to a document of that module
  """
  def __init__(self, threshold, getDuration, prefix=1, error_detail=False):
    super(ERP5SiteStats, self).__init__(threshold, getDuration, prefix=prefix,
      error_detail=error_detail)
    # Key levels:
    # - module id (string)
    # - is document (bool)
    # - date (string)
    self.module = defaultdict(partial(defaultdict, partial(
      defaultdict, partial(APDEXStats, threshold, getDuration))))
    self.no_module = defaultdict(partial(APDEXStats, threshold, getDuration))

  def accumulate(self, match, url_match, date):
    prefix = self.prefix
    split = url_match.group('url').split('?', 1)[0].split('/')[1 + prefix:]
    if split:
      module = split[0]
      if module.endswith('_module'):
        super(ERP5SiteStats, self).accumulate(match, url_match, date)
        self.module[module][
          len(split) > 1 and (split[1] != 'view' and '_view' not in split[1])
        ][date].accumulate(match)
      else:
        self.no_module[date].accumulate(match)

  def asHTML(self, stat_filter=lambda x: x):
    result = []
    append = result.append
    append('<h2>Stats per module</h2><table class="stats"><tr>'
      '<th rowspan="2" colspan="2">module</th><th colspan="4">overall</th>')
    filtered_module = defaultdict(partial(defaultdict, partial(
      defaultdict, partial(APDEXStats, self.threshold, None))))
    filtered_no_module = defaultdict(partial(APDEXStats, self.threshold, None))
    for date, value in self.no_module.iteritems():
      filtered_no_module[stat_filter(date)].accumulateFrom(value)
    column_set = set(filtered_no_module)
    for key, is_document_dict in self.module.iteritems():
      filtered_is_document_dict = filtered_module[key]
      for key, data_dict in is_document_dict.iteritems():
        filtered_data_dict = filtered_is_document_dict[key]
        for date, value in data_dict.iteritems():
          filtered_data_dict[stat_filter(date)].accumulateFrom(value)
        column_set.update(filtered_data_dict)
    column_list = sorted(column_set)
    for date in column_list:
      append('<th colspan="4">%s</th>' % date)
    append('</tr><tr>')
    for _ in xrange(len(column_list) + 1):
      append(APDEX_TABLE_HEADERS)
    append('</tr>')
    def apdexAsColumns(data_dict):
      data_total = APDEXStats(self.threshold, None)
      for data in data_dict.values():
        data_total.accumulateFrom(data)
      append(getApdexStatsAsHtml(data_total, self.threshold))
      for date in column_list:
        append(getApdexStatsAsHtml(data_dict[date], self.threshold))
    for module_id, data_dict in sorted(filtered_module.iteritems(),
        key=ITEMGETTER0):
      append('<tr><th rowspan="2">%s</th><th>module</th>' % module_id)
      apdexAsColumns(data_dict[False])
      append('</tr><tr><th>document</th>')
      apdexAsColumns(data_dict[True])
      append('</tr>')
    append('<tr><th colspan="2">(none)</th>')
    apdexAsColumns(filtered_no_module)
    append('</tr></table>')
    append(super(ERP5SiteStats, self).asHTML(stat_filter=stat_filter))
    return '\n'.join(result)

DURATION_US_FORMAT = '%D'
DURATION_S_FORMAT = '%T'

logformat_dict = {
  '%h': r'(?P<host>[^ ]*)',
  '%l': r'(?P<ident>[^ ]*)',
  '%u': r'(?P<user>[^ ]*)',
  '%t': r'\[(?P<timestamp>[^\]]*)\]',
  '%r': r'(?P<request>(\\.|[^\\"])*)', # XXX: expected to be enclosed in ". See also REQUEST_PATTERN
  '%>s': r'(?P<status>[0-9]*?)',
  '%O': r'(?P<size>[0-9-]*?)',
  '%{Referer}i': r'(?P<referer>[^"]*)', # XXX: expected to be enclosed in "
  '%{User-Agent}i': r'(?P<agent>[^"]*)', # XXX: expected to be enclosed in "
  DURATION_US_FORMAT: r'(?P<duration>[0-9]*)',
  DURATION_S_FORMAT: r'(?P<duration_s>[0-9]*)',
  '%%': r'%',
  # TODO: add more formats
}

REQUEST_PATTERN = re.compile('(?P<method>[^ ]*) (?P<url>[^ ]*)'
  '( (?P<protocol>.*))?')

class AggregateSiteUrl(argparse.Action):
  __argument_to_aggregator = {
      '--base': GenericSiteStats,
      '--erp5-base': ERP5SiteStats,
      '--skip-base': None,
  }
  def __call__(self, parser, namespace, values, option_string=None):
    action = self.__argument_to_aggregator[option_string]
    dest = getattr(namespace, self.dest)
    for value in values:
      if action is not None:
        if value[-1:] == '/':
          offset = -1
        else:
          offset = 0
        action = partial(action, prefix=value.count('/') + offset)
      dest.append((value, action))

def _asMonthString(timestamp):
  dt, tz = timestamp.split(' ')
  _, month, year = dt.split(':', 1)[0].split('/')
  return '%s/%02i' % (year, MONTH_VALUE_DICT[month])

def _asDayString(timestamp):
  dt, tz = timestamp.split(' ')
  day, month, year = dt.split(':', 1)[0].split('/')
  return '%s/%02i/%s' % (year, MONTH_VALUE_DICT[month], day)

def _asHourString(timestamp):
  dt, tz = timestamp.split(' ')
  date, hour, _ = dt.split(':', 2)
  day, month, year = date.split('/')
  return '%s/%02i/%s %s' % (year, MONTH_VALUE_DICT[month], day, hour)

# Key: argument (represents table granularity)
# Value:
# - cheap conversion from apache date format to graph granularity
#   must be sortable consistently with time flow
# - conversion from gaph granularity to table granularity
# - graph granularity caption
# - format string to parse and generate graph granularity into/from
#   datetime.datetime instance
# - period during which a placeholder point will be added if there is no data
#   point
period_parser = {
  'year': (
    _asMonthString,
    lambda x: x.split('/', 1)[0],
    'month',
    '%Y/%m',
    # Longest month: 31 days
    timedelta(31),
  ),
  'month': (
    _asDayString,
    lambda x: '/'.join(x.split('/', 2)[:2]),
    'day',
    '%Y/%m/%d',
    # Longest day: 24 hours + 1h DST (never more ?)
    timedelta(seconds=3600 * 25),
  ),
  'day': (
    _asHourString,
    lambda x: x.split(' ')[0],
    'hour',
    '%Y/%m/%d %H',
    # Longest hour: 60 * 60 seconds + 1 leap second.
    timedelta(seconds=3601),
  ),
}

def main():
  global abs_file_container
  parser = argparse.ArgumentParser(description='Compute Apdex out of '
    'apache-style log files')
  parser.add_argument('logfile', nargs='+',
    help='Log files to process')
  parser.add_argument('-l', '--logformat',
    default='%h %l %u %t "%r" %>s %O "%{Referer}i" "%{User-Agent}i" %D',
    help='Apache LogFormat used to generate provided logs. '
      'Default: %(default)r')
  parser.add_argument('-o', '--out', default='-',
    help='Filename to write output to. Use - for stdout. Default: %(default)s')
  parser.add_argument('-q', '--quiet', action='store_true',
    help='Suppress warnings about malformed lines.')

  group = parser.add_argument_group('generated content')
  group.add_argument('-a', '--apdex', default=1.0, type=float,
    help='First threshold for Apdex computation, in seconds. '
      'Default: %(default).2fs')
  group.add_argument('-e', '--error-detail', action='store_true',
    help='Include detailed report (url & referers) for error statuses.')
  group.add_argument('-p', '--period', default='day', choices=period_parser,
      help='Periodicity of sampling buckets. Default: %(default)r')
  group.add_argument('-s', '--stats', action='store_true',
    help='Enable parsing stats (time spent parsing input, time spent '
      'generating output, ...)')
  if abs_file_container is not None:
    # Force embedding when file container is unknown (ex: pkg_resources).
    # XXX: allow when --js is also provided ?
    group.add_argument('--js', default=abs_file_container,
      help='Folder containing needed js files. Default: %(default)s')
    group.add_argument('--js-embed', action='store_true',
      help='Embed js files instead of linking to them.')

  group = parser.add_argument_group('site matching', 'Earlier arguments take '
    'precedence. For example: --skip-base /foo/bar --base /foo generates '
    'stats for /foo, excluding /foo/bar.')
  group.add_argument('-d', '--default',
    help='Caption for lines matching no prefix, or skip them if not provided.')
  group.add_argument('--base', dest='path', default=[], nargs='+',
    action=AggregateSiteUrl,
    help='Absolute base url(s) of some part of a site.')
  group.add_argument('--erp5-base', dest='path', nargs='+',
    action=AggregateSiteUrl,
    help='Absolute base url(s) of some part of an ERP5 site (more '
    'specific stats than --base).')
  group.add_argument('--skip-base', dest='path', nargs='+',
    action=AggregateSiteUrl,
    help='Absolute base url(s) to ignore.')

  group = parser.add_argument_group('filtering')
  group.add_argument('--skip-user-agent', nargs='+', default=[],
    action='append', help='List of user agents from which hits should be '
      'ignored. Useful to exclude monitoring systems.')

  args = parser.parse_args()
  abs_file_container = getattr(args, 'js', abs_file_container)
  if DURATION_US_FORMAT in args.logformat:
    getDuration = lambda x: int(x.group('duration'))
  elif DURATION_S_FORMAT in args.logformat:
    getDuration = lambda x: int(x.group('duration_s')) * US_PER_S
  else:
    print >> sys.stderr, 'Neither %D nor %T are present in logformat, apdex ' \
      'cannot be computed.'
    sys.exit(1)
  line_regex = ''
  try:
    n = iter(args.logformat).next
    while True:
      key = None
      char = n()
      if char == '%':
        fmt = n()
        key = char + fmt
        if fmt == '{':
          while fmt != '}':
            fmt = n()
            key += fmt
          key += n()
        elif fmt == '>':
          key += n()
        char = logformat_dict[key]
      line_regex += char
  except StopIteration:
    assert not key, key
  matchline = re.compile(line_regex).match
  matchrequest = REQUEST_PATTERN.match
  asDate, decimator, graph_period, date_format, placeholder_delta = \
    period_parser[args.period]
  site_list = args.path
  default_site = args.default
  if default_site is None:
    default_action = None
    if not [None for _, x in site_list if x is not None]:
      print >> sys.stderr, 'None of --default, --erp5-base and --base were ' \
        'specified, nothing to do.'
      sys.exit(1)
  else:
    default_action = partial(GenericSiteStats, prefix=0)
  infile_list = args.logfile
  quiet = args.quiet
  threshold = args.apdex
  error_detail = args.error_detail
  file_count = len(infile_list)
  per_site = {}
  hit_per_day = defaultdict(int)
  skip_user_agent = list(itertools.chain(*args.skip_user_agent))
  malformed_lines = 0
  skipped_lines = 0
  no_url_lines = 0
  all_lines = 0
  skipped_user_agent = 0
  start_time = time.time()
  for fileno, filename in enumerate(infile_list, 1):
    print >> sys.stderr, 'Processing %s [%i/%i]' % (
      filename, fileno, file_count)
    logfile = gzip.open(filename)
    try:
      logfile.readline()
    except IOError:
      logfile = open(filename)
    else:
      logfile.seek(0)
    lineno = 0
    for lineno, line in enumerate(logfile, 1):
      if lineno % 5000 == 0:
        sys.stderr.write('%i\r' % lineno)
        sys.stderr.flush()
      match = matchline(line)
      if match is None:
        if not quiet:
          print >> sys.stderr, 'Malformed line at %s:%i: %r' % (
            filename, lineno, line)
        malformed_lines += 1
        continue
      if match.group('agent') in skip_user_agent:
        skipped_user_agent += 1
        continue
      url_match = matchrequest(match.group('request'))
      if url_match is None:
        no_url_lines += 1
        continue
      url = url_match.group('url')
      if url.startswith('http'):
        url = splithost(splittype(url)[1])[1]
      startswith = url.startswith
      for site, action in site_list:
        if startswith(site):
          break
      else:
        site = default_site
        action = default_action
      if action is None:
        skipped_lines += 1
        continue
      date = asDate(match.group('timestamp'))
      hit_per_day[decimator(date)] += 1
      try:
        site_data = per_site[site]
      except KeyError:
        site_data = per_site[site] = action(threshold, getDuration,
          error_detail=error_detail)
      site_data.accumulate(match, url_match, date)
    all_lines += lineno
    sys.stderr.write('%i\n' % lineno)
  end_parsing_time = time.time()
  if args.out == '-':
    out = sys.stdout
  else:
    out = open(args.out, 'w')
  with out:
    out.write('<html><head><title>Stats</title><style>'
      '.stats th, .stats td { border: solid 1px #000; } '
      '.stats th { text-align: center; } '
      '.stats td { text-align: right; } '
      '.stats th.text, .stats td.text { text-align: left; } '
      '.stats td.no_hit { color: #ccc; } '
      'table.stats { border-collapse: collapse; } '
      '.problem { background-color: #f00; color: white; } '
      '.warning { background-color: #f80; color: white; } '
      'h1 { background-color: #ccc; } '
      'h2 { background-color: #eee; } '
      '.axisLabels { color: rgb(84,84,84) !important; }'
      '.flot-x-axis .tickLabel { text-align: center; } '
      '</style>')
    for script in ('jquery.js', 'jquery.flot.js', 'jquery.flot.time.js',
        'jquery.flot.axislabels.js'):
      if getattr(args, 'js_embed', True):
        out.write('<script type="text/javascript">//<![CDATA[\n')
        out.write(getResource(script))
        out.write('\n//]]></script>')
      else:
        out.write('<script type="text/javascript" src="%s/%s"></script>' % (
          args.js, script))
    out.write('<script type="text/javascript">$(function() {'
      '$(".graph").each(function (i){'
        '$.plot('
          'this,'
          '$.parseJSON($(this).attr("data-points")),'
          '$.parseJSON($(this).attr("data-options")));'
      '});'
    '});</script>')
    out.write('</head><body><h1>Overall</h1><h2>Parameters</h2>'
      '<table class="stats">')
    for caption, value in (
          ('apdex threshold', '%.2fs' % args.apdex),
          ('period', args.period),
        ):
      out.write('<tr><th class="text">%s</th><td>%s</td></tr>' % (
        caption, value))
    out.write('</table><h2>Hits per period</h2><table class="stats">'
      '<tr><th>date</th><th>hits</th></tr>')
    for date, hit in sorted(hit_per_day.iteritems(), key=ITEMGETTER0):
      out.write('<tr><td>%s</td><td>%s</td></tr>' % (date, hit))
    out.write('</table>')
    def graph(title, data, options={}):
      out.write('<h2>%s</h2><div class="graph" '
        'style="width:600px;height:300px" data-points="' % title)
      out.write(escape(json.dumps(data), quote=True))
      out.write('" data-options="')
      out.write(escape(json.dumps(options), quote=True))
      out.write('"></div>')
    for site_id, data in per_site.iteritems():
      out.write('<h1>Site: %s</h1>' % site_id)
      daily_data = data.getApdexData()
      current_date = datetime.strptime(daily_data[0][0], date_format)
      new_daily_data = []
      append = new_daily_data.append
      for measure in daily_data:
        measure_date = datetime.strptime(measure[0], date_format)
        while current_date < measure_date:
          append((current_date.strftime(date_format), 100, 0))
          current_date += placeholder_delta
        append(measure)
        current_date = measure_date + placeholder_delta
      daily_data = new_daily_data
      date_list = [int(time.mktime(time.strptime(x[0], date_format)) * 1000)
        for x in daily_data]
      timeformat = '%Y<br/>%m/%d<br/>%H:%M'
      # There is room for about 10 labels on the X axis.
      minTickSize = (max(1,
        (date_list[-1] - date_list[0]) / (60 * 60 * 1000 * 10)), 'hour')
      # Guesstimation: 6px per digit. If only em were allowed...
      yLabelWidth = max(int(math.log10(max(x[2] for x in daily_data))) + 1,
        3) * 6
      graph('apdex',
        [zip(date_list, (x[1] for x in daily_data))],
        {
          'xaxis': {
            'mode': 'time',
            'timeformat': timeformat,
            'minTickSize': minTickSize,
          },
          'yaxis': {
            'max': 100,
            'axisLabel': '%',
            'labelWidth': yLabelWidth,
          },
          'lines': {'show': True},
        },
      )
      graph('Hits (per %s)' % graph_period,
        [zip(date_list, (x[2] for x in daily_data))],
        {
          'xaxis': {
            'mode': 'time',
            'timeformat': timeformat,
            'minTickSize': minTickSize,
          },
          'yaxis': {
            'axisLabel': 'Hits',
            'labelWidth': yLabelWidth,
            'tickDecimals': 0,
          },
          'lines': {'show': True},
        },
      )
      out.write(data.asHTML(decimator))
    end_stat_time = time.time()
    if args.stats:
      out.write('<h1>Parsing stats</h1><table class="stats">')
      buildno, builddate = platform.python_build()
      parsing_time = end_parsing_time - start_time
      for caption, value in (
            ('Execution date', datetime.now().isoformat()),
            ('Interpreter', '%s %s build %s (%s)' % (
              platform.python_implementation(),
              platform.python_version(),
              buildno,
              builddate,
            )),
            ('File count', file_count),
            ('Lines', all_lines),
            ('... malformed', malformed_lines),
            ('... URL-less', no_url_lines),
            ('... skipped (URL)', skipped_lines),
            ('... skipped (user agent)', skipped_user_agent),
            ('Parsing time', timedelta(seconds=parsing_time)),
            ('Parsing rate', '%i line/s' % (all_lines / parsing_time)),
            ('Rendering time', timedelta(seconds=(
              end_stat_time - end_parsing_time))),
          ):
        out.write('<tr><th class="text">%s</th><td>%s</td></tr>' % (
          caption, value))
      out.write('</table>')
    out.write('</body></html>')

if __name__ == '__main__':
  main()
