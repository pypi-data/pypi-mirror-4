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
from datetime import datetime, timedelta, date
from functools import partial
from operator import itemgetter
from urllib import splittype, splithost, unquote
import argparse
import bz2
import calendar
import codecs
import gzip
import httplib
import itertools
import json
import math
import os
import platform
import re
import shlex
import sys
import time
import traceback
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

FILE_OPENER_LIST = [
  (gzip.open, IOError),
  (bz2.BZ2File, IOError),
]

try:
  from backports import lzma
except ImportError:
  pass
else:
  FILE_OPENER_LIST.append((lzma.open, lzma._lzma.LZMAError))

MONTH_VALUE_DICT = dict((y, x) for (x, y) in enumerate(('Jan', 'Feb', 'Mar',
  'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'), 1))

US_PER_S = 10 ** 6

N_SLOWEST = 20
N_ERROR_URL = 10
N_REFERRER_PER_ERROR_URL = 5
N_USER_AGENT = 20
ITEMGETTER0 = itemgetter(0)
ITEMGETTER1 = itemgetter(1)
APDEX_TOLERATING_COEF = 4
AUTO_PERIOD_COEF = 200

# Larger (x < LARGER_THAN_INTEGER_STR == True) than any string starting with
# a number
LARGER_THAN_INTEGER_STR = 'A'

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

def getDataPoints(apdex_dict):
  return [
    (value_date, apdex.getApdex() * 100, apdex.hit) for value_date, apdex
    in sorted(apdex_dict.iteritems(), key=ITEMGETTER0)]

def prepareDataForGraph(daily_data, date_format, placeholder_delta,
    coefficient_callback, x_min=None, x_max=None):
  current_date = datetime.strptime(x_min or daily_data[0][0], date_format)
  new_daily_data = []
  append = new_daily_data.append
  for (measure_date_string, apdex, hit) in daily_data:
    measure_date = datetime.strptime(measure_date_string, date_format)
    if current_date < measure_date:
      append((current_date.strftime(date_format), 100, 0))
      placeholder_end_date = measure_date - placeholder_delta
      if placeholder_end_date > current_date:
        append((placeholder_end_date.strftime(date_format), 100, 0))
    append((measure_date_string, apdex,
      hit * coefficient_callback(measure_date)))
    current_date = measure_date + placeholder_delta
  if x_max is not None and current_date < datetime.strptime(x_max,
      date_format):
    append((current_date.strftime(date_format), 100, 0))
    append((x_max, 100, 0))
  return new_daily_data

def graphPair(daily_data, date_format, graph_period, apdex_y_min=None,
    hit_y_min=None, hit_y_max=None, apdex_y_scale=None):
  date_list = [int(calendar.timegm(time.strptime(x[0], date_format)) * 1000)
    for x in daily_data]
  timeformat = '%Y/<br/>%m/%d<br/> %H:%M'
  # There is room for about 10 labels on the X axis.
  minTickSize = (max(1,
    (date_list[-1] - date_list[0]) / (60 * 60 * 1000 * 10)), 'hour')
  # Guesstimation: 6px per digit. If only em were allowed...
  yLabelWidth = max(int(math.log10(max(x[2] for x in daily_data))) + 1,
    3) * 6
  return graph('apdex',
    [zip(date_list, (round(x[1], 2) for x in daily_data))],
    {
      'xaxis': {
        'mode': 'time',
        'timeformat': timeformat,
        'minTickSize': minTickSize,
      },
      'yaxis': {
        'min': apdex_y_min,
        'max': 100,
        'axisLabel': 'apdex (%)',
        'labelWidth': yLabelWidth,
        'transform': apdex_y_scale,
      },
      'lines': {'show': True},
      'grid': {
        'hoverable': True,
      },
    },
  ) + graph('Hits (per %s)' % graph_period,
    [zip(date_list, (x[2] for x in daily_data))],
    {
      'xaxis': {
        'mode': 'time',
        'timeformat': timeformat,
        'minTickSize': minTickSize,
      },
      'yaxis': {
        'min': hit_y_min,
        'max': hit_y_max,
        'axisLabel': 'Hits',
        'labelWidth': yLabelWidth,
        'tickDecimals': 0,
      },
      'lines': {'show': True},
      'grid': {
        'hoverable': True,
      },
    },
  )

def graph(title, data, options={}):
  result = []
  append = result.append
  append('<h2>%s</h2><div class="graph" '
    'style="width:600px;height:300px" data-points="' % title)
  append(escape(json.dumps(data), quote=True))
  append('" data-options="')
  append(escape(json.dumps(options), quote=True))
  append('"></div><div class="tooltip">'
    '<span class="x"></span><br/>'
    '<span class="y"></span></div>')
  return ''.join(result)

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

  @staticmethod
  def asHTMLHeader(overall=False):
    return '<th>apdex</th><th>hits</th><th>avg (s)</th>' \
      '<th%s>max (s)</th>' % (overall and ' class="overall_right"' or '')

  def asHTML(self, threshold, overall=False):
    apdex = self.getApdex()
    average = self.getAverage()
    maximum = self.getMax()
    hit = self.hit
    if hit:
      extra_class = ''
      apdex_style = 'color: #%s; background-color: #%s' % (
        (apdex < .5 and 'f' or '0') * 3,
        ('%x' % (apdex * 0xf)) * 3,
      )
    else:
      extra_class = 'no_hit'
      apdex_style = ''
    if overall:
      extra_right_class = 'overall_right'
    else:
      extra_right_class = ''
    return '<td style="%(apdex_style)s" class="%(extra_class)s group_left">' \
      '%(apdex)i%%</td><td class="%(extra_class)s">%(hit)s</td>' \
      '<td class="%(average_class)s %(extra_class)s">%(average).2f</td>' \
      '<td class="%(max_class)s %(extra_class)s group_right ' \
      '%(extra_right_class)s">%(max).2f</td>' % {
      'extra_class': extra_class,
      'apdex_style': apdex_style,
      'apdex': round(apdex * 100),
      'hit': hit,
      'average_class': getClassForDuration(average, threshold),
      'average': average,
      'max_class': getClassForDuration(maximum, threshold),
      'max': maximum,
      'extra_right_class': extra_right_class,
    }

  @classmethod
  def fromJSONState(cls, state, getDuration):
    result = cls(0, getDuration)
    result.__dict__.update(state)
    return result

  def asJSONState(self):
    result = self.__dict__.copy()
    del result['getDuration']
    return result

_APDEXDateDictAsJSONState = lambda date_dict: dict(((y, z.asJSONState())
  for y, z in date_dict.iteritems()))

class GenericSiteStats(object):
  def __init__(self, threshold, getDuration, suffix, error_detail=False):
    self.threshold = threshold
    self.suffix = suffix
    self.error_detail = error_detail
    self.status = defaultdict(partial(defaultdict, int))
    if error_detail:
      self.error_url_count = defaultdict(partial(defaultdict, list))
    self.url_apdex = defaultdict(partial(APDEXStats, threshold, getDuration))
    self.apdex = defaultdict(partial(APDEXStats, threshold, getDuration))
    self.user_agent_counter = Counter()

  def rescale(self, convert, getDuration):
    for status, date_dict in self.status.iteritems():
      new_date_dict = defaultdict(int)
      for value_date, status_count in date_dict.iteritems():
        new_date_dict[convert(value_date)] += status_count
      self.status[status] = new_date_dict
    new_apdex = defaultdict(partial(APDEXStats, self.threshold, getDuration))
    for value_date, data in self.apdex.iteritems():
      new_apdex[convert(value_date)].accumulateFrom(data)
    self.apdex = new_apdex

  def accumulate(self, match, url_match, value_date):
    self.apdex[value_date].accumulate(match)
    if url_match is None:
      url = match.group('request')
    else:
      url = url_match.group('url')
    # XXX: can eat memory if there are many different urls
    self.url_apdex[url.split('?', 1)[0]].accumulate(match)
    status = match.group('status')
    self.status[status][value_date] += 1
    if self.error_detail and statusIsError(status):
      # XXX: can eat memory if there are many errors on many different urls
      self.error_url_count[status][url].append(match.group('referer'))
    self.user_agent_counter[match.group('agent')] += 1

  def getApdexData(self):
    return getDataPoints(self.apdex)

  def asHTML(self, date_format, placeholder_delta, graph_period,
      graph_coefficient, encoding, stat_filter=lambda x: x,
      x_min=None, x_max=None,
      apdex_y_min=None, hit_y_min=None, hit_y_max=None,
      apdex_y_scale=None,
    ):
    result = []
    append = result.append
    apdex = APDEXStats(self.threshold, None)
    for data in self.apdex.itervalues():
      apdex.accumulateFrom(data)
    append('<h2>Overall</h2><table class="stats"><tr>')
    append(APDEXStats.asHTMLHeader())
    append('</tr><tr>')
    append(apdex.asHTML(self.threshold))
    append('</tr></table><h2>Hottest pages</h2><table class="stats"><tr>')
    append(APDEXStats.asHTMLHeader())
    append('<th>url</th></tr>')
    for url, data in sorted(self.url_apdex.iteritems(), key=lambda x: x[1].getAverage() * x[1].hit,
        reverse=True)[:N_SLOWEST]:
      append('<tr>')
      append(data.asHTML(self.threshold))
      append('<td class="text">%s</td></tr>' % unquoteToHtml(url, encoding))
    append('</table>')
    append('<h2>User agents</h2><table class="stats"><tr><th>hits</th>'
      '<th>user agent</th></tr>')
    for user_agent, hit in self.user_agent_counter.most_common(N_USER_AGENT):
      # XXX: s/escape/unquoteToHtml/ ?
      append('<tr><td>%s</td><td class="text">%s</td></tr>' % (hit, escape(user_agent)))
    append('</table>')
    column_set = set()
    filtered_status = defaultdict(partial(defaultdict, int))
    for status, date_dict in self.status.iteritems():
      filtered_date_dict = filtered_status[status]
      for value_date, value in date_dict.iteritems():
        filtered_date_dict[stat_filter(value_date)] += value
      column_set.update(filtered_date_dict)
    column_list = sorted(column_set)
    append('<h2>Hits per status code</h2><table class="stats"><tr>'
      '<th>status</th><th>overall</th>')
    for column in column_list:
      append('<th>%s</th>' % column)
    append('</tr>')
    def hitTd(hit, status):
      return '<td class="%s">%s</td>' % (getClassForStatusHit(hit, status), hit)
    def statusAsHtml(status):
      try:
        definition = httplib.responses[int(status)]
      except KeyError:
        return status
      else:
        return '<abbr title="%s">%s</abbr>' % (definition, status)
    has_errors = False
    for status, data_dict in sorted(filtered_status.iteritems(),
        key=ITEMGETTER0):
      has_errors |= statusIsError(status)
      append('<tr><th>%s</th>' % statusAsHtml(status))
      append(hitTd(sum(data_dict.itervalues()), status))
      for column in column_list:
        append(hitTd(data_dict[column], status))
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
        append('<tr><th rowspan="%s">%s</th>' % (len(url_list),
          statusAsHtml(status)))
        first_url = True
        for url, referer_counter in url_list:
          if first_url:
            first_url = False
          else:
            append('<tr>')
          append('<td>%s</td><td class="text">%s</td>'
            '<td class="text">%s</td>' % (
            getHitForUrl(referer_counter),
            unquoteToHtml(url, encoding),
            '<br/>'.join('%i: %s' % (hit, unquoteToHtml(referer, encoding))
              for referer, hit in sorted(
                referer_counter.iteritems(),
                key=ITEMGETTER1,
                reverse=True,
            )[:N_REFERRER_PER_ERROR_URL]),
          ))
          append('</tr>')
      append('</table>')
    return '\n'.join(result)

  @classmethod
  def fromJSONState(cls, state, getDuration, suffix):
    error_detail = state['error_detail']
    result = cls(state['threshold'], getDuration, suffix, error_detail)
    if error_detail:
      error_url_count = result.error_url_count
      for state_status, state_url_dict in state['error_url_count'].iteritems():
        error_url_count[state_status].update(state_url_dict)
    for attribute_id in ('url_apdex', 'apdex'):
      attribute = getattr(result, attribute_id)
      for key, apdex_state in state[attribute_id].iteritems():
        attribute[key] = APDEXStats.fromJSONState(apdex_state, getDuration)
    status = result.status
    for status_code, date_dict in state['status'].iteritems():
      status[status_code].update(date_dict)
    result.user_agent_counter.update(state['user_agent_counter'])
    return result

  def asJSONState(self):
    return {
      'threshold': self.threshold,
      'error_detail': self.error_detail,
      'error_url_count': getattr(self, 'error_url_count', None),
      'url_apdex': _APDEXDateDictAsJSONState(self.url_apdex),
      'apdex': _APDEXDateDictAsJSONState(self.apdex),
      'status': self.status,
      'user_agent_counter': self.user_agent_counter,
    }

  def accumulateFrom(self, other):
    # XXX: ignoring: threshold, getDuration, suffix, error_detail.
    # Assuming they are consistently set.
    if self.error_detail:
      for status, other_url_dict in other.error_url_count.iteritems():
        url_dict = self.error_url_count[status]
        for url, referer_list in other_url_dict.iteritems():
          url_dict[url].extend(referer_list)
    for attribute_id in ('url_apdex', 'apdex'):
      self_attribute = getattr(self, attribute_id)
      for key, apdex_data in getattr(other, attribute_id).iteritems():
        self_attribute[key].accumulateFrom(apdex_data)
    status = self.status
    for status_code, other_date_dict in other.status.iteritems():
      date_dict = status[status_code]
      for status_date, count in other_date_dict.iteritems():
        date_dict[status_date] += count
    self.user_agent_counter.update(other.user_agent_counter)

class ERP5SiteStats(GenericSiteStats):
  """
  Heuristic used:
  - ignore any GET parameter
  - If the first in-site url chunk ends with "_module", count line as
    belonging to a module
  - If a line belongs to a module and has at least 2 slashes after module,
    count line as belonging to a document of that module
  """
  def __init__(self, threshold, getDuration, suffix, error_detail=False):
    super(ERP5SiteStats, self).__init__(threshold, getDuration, suffix,
      error_detail=error_detail)
    # Key levels:
    # - module id (string)
    # - is document (bool)
    # - date (string)
    self.module = defaultdict(partial(defaultdict, partial(
      defaultdict, partial(APDEXStats, threshold, getDuration))))
    self.no_module = defaultdict(partial(APDEXStats, threshold, getDuration))
    self.site_search = defaultdict(partial(APDEXStats, threshold, getDuration))

  def rescale(self, convert, getDuration):
    super(ERP5SiteStats, self).rescale(convert, getDuration)
    threshold = self.threshold
    for document_dict in self.module.itervalues():
      for is_document, date_dict in document_dict.iteritems():
        new_date_dict = defaultdict(partial(APDEXStats, threshold, getDuration))
        for value_date, data in date_dict.iteritems():
          new_date_dict[convert(value_date)].accumulateFrom(data)
        document_dict[is_document] = new_date_dict
    for attribute_id in ('no_module', 'site_search'):
      attribute = defaultdict(partial(APDEXStats, threshold, getDuration))
      for value_date, data in getattr(self, attribute_id).iteritems():
        attribute[convert(value_date)].accumulateFrom(data)
      setattr(self, attribute_id, attribute)

  def accumulate(self, match, url_match, value_date):
    split = self.suffix(url_match.group('url')).split('?', 1)[0].split('/')
    if split and split[0].endswith('_module'):
      super(ERP5SiteStats, self).accumulate(match, url_match, value_date)
      module = split[0]
      self.module[module][
        len(split) > 1 and (split[1] != 'view' and '_view' not in split[1])
      ][value_date].accumulate(match)
    elif split and split[0] == 'ERP5Site_viewSearchResult':
      super(ERP5SiteStats, self).accumulate(match, url_match, value_date)
      self.site_search[value_date].accumulate(match)
    else:
      self.no_module[value_date].accumulate(match)

  def asHTML(self, date_format, placeholder_delta, graph_period, graph_coefficient,
      encoding, stat_filter=lambda x: x, x_min=None, x_max=None,
      apdex_y_min=None, hit_y_min=None, hit_y_max=None,
      apdex_y_scale=None,
    ):
    result = []
    append = result.append
    append('<h2>Stats per module</h2><table class="stats stats_erp5"><tr>'
      '<th rowspan="2" colspan="3">module</th>'
      '<th colspan="4" class="overall_right">overall</th>')
    module_document_overall = defaultdict(partial(APDEXStats, self.threshold,
      None))
    filtered_module = defaultdict(partial(defaultdict, partial(
      defaultdict, partial(APDEXStats, self.threshold, None))))
    filtered_no_module = defaultdict(partial(APDEXStats, self.threshold, None))
    for value_date, value in self.no_module.iteritems():
      filtered_no_module[stat_filter(value_date)].accumulateFrom(value)
    column_set = set(filtered_no_module)
    filtered_site_search = defaultdict(partial(APDEXStats, self.threshold,
      None))
    for value_date, value in self.site_search.iteritems():
      filtered_site_search[stat_filter(value_date)].accumulateFrom(value)
    column_set.update(filtered_site_search)
    for key, is_document_dict in self.module.iteritems():
      filtered_is_document_dict = filtered_module[key]
      for key, data_dict in is_document_dict.iteritems():
        filtered_data_dict = filtered_is_document_dict[key]
        module_document_apdex = module_document_overall[key]
        for value_date, value in data_dict.iteritems():
          filtered_data_dict[stat_filter(value_date)].accumulateFrom(value)
          module_document_apdex.accumulateFrom(value)
        column_set.update(filtered_data_dict)
    column_list = sorted(column_set)
    for column in column_list:
      append('<th colspan="4">%s</th>' % column)
    append('</tr><tr>')
    for i in xrange(len(column_list) + 1):
      append(APDEXStats.asHTMLHeader(i == 0))
    append('</tr>')
    def apdexAsColumns(data_dict):
      data_total = APDEXStats(self.threshold, None)
      for data in data_dict.values():
        data_total.accumulateFrom(data)
      append(data_total.asHTML(self.threshold, True))
      for column in column_list:
        append(data_dict[column].asHTML(self.threshold))
      return data_total
    def hiddenGraph(data_dict, title):
      append('<td class="text group_right hidden_graph">')
      data = getDataPoints(data_dict)
      if len(data) > 1:
        append('<span class="action" onclick="toggleGraph(this)">+</span>'
          '<div class="positioner"><div class="container">'
          '<div class="title">%s</div>'
          '<div class="action close" onclick="hideGraph(this)">close</div>' %
          title
        )
        append(graphPair(
          prepareDataForGraph(
            data,
            date_format,
            placeholder_delta,
            graph_coefficient,
            x_min=x_min,
            x_max=x_max,
          ),
          date_format,
          graph_period,
          apdex_y_min=apdex_y_min,
          hit_y_min=hit_y_min,
          hit_y_max=hit_y_max,
          apdex_y_scale=apdex_y_scale,
        ))
        append('</div></div>')
      append('</td>')
    for module_id, data_dict in sorted(filtered_module.iteritems(),
        key=ITEMGETTER0):
      append('<tr class="group_top"><th rowspan="2">%s</th>'
        '<th>module</th>' % module_id)
      hiddenGraph(self.module[module_id][False], module_id + ' (module)')
      apdexAsColumns(data_dict[False])
      append('</tr><tr class="group_bottom"><th>document</th>')
      hiddenGraph(self.module[module_id][True], module_id + '  (document)')
      apdexAsColumns(data_dict[True])
      append('</tr>')
    append('<tr class="group_top group_bottom"><th colspan="2">site search'
      '</th>')
    hiddenGraph(self.site_search, 'site search')
    site_search_overall = apdexAsColumns(filtered_site_search)
    append('<tr class="group_top group_bottom"><th colspan="2">other</th>')
    hiddenGraph(self.no_module, 'other')
    no_module_overall = apdexAsColumns(filtered_no_module)
    append('</tr></table><h2>Per-level overall</h2><table class="stats"><tr>'
      '<th>level</th>')
    append(APDEXStats.asHTMLHeader())
    append('</tr><tr><th>other</th>')
    append(no_module_overall.asHTML(self.threshold))
    append('</tr><tr><th>site search</th>')
    append(site_search_overall.asHTML(self.threshold))
    append('</tr><tr><th>module</th>')
    append(module_document_overall[False].asHTML(self.threshold))
    append('</tr><tr><th>document</th>')
    append(module_document_overall[True].asHTML(self.threshold))
    append('</tr></table>')
    append(super(ERP5SiteStats, self).asHTML(date_format,
      placeholder_delta, graph_period, graph_coefficient, encoding,
      stat_filter=stat_filter,
      x_min=x_min, x_max=x_max,
      apdex_y_min=apdex_y_min, hit_y_min=hit_y_min, hit_y_max=hit_y_max,
      apdex_y_scale=apdex_y_scale,
    ))
    return '\n'.join(result)

  @classmethod
  def fromJSONState(cls, state, getDuration, suffix):
    result = super(ERP5SiteStats, cls).fromJSONState(state, getDuration, suffix)
    for module_id, module_dict_state in state['module'].iteritems():
      module_dict = result.module[module_id]
      for is_document, date_dict_state in module_dict_state.iteritems():
        date_dict = module_dict[is_document == 'true']
        for value_date, apdex_state in date_dict_state.iteritems():
          date_dict[value_date] = APDEXStats.fromJSONState(apdex_state, getDuration)
    for attribute_id in ('no_module', 'site_search'):
      attribute = getattr(result, attribute_id)
      for value_date, apdex_state in state[attribute_id].iteritems():
        attribute[value_date] = APDEXStats.fromJSONState(apdex_state, getDuration)
    return result

  def asJSONState(self):
    result = super(ERP5SiteStats, self).asJSONState()
    result['module'] = module = {}
    for module_id, module_dict in self.module.iteritems():
      module_dict_state = module[module_id] = {}
      for is_document, date_dict in module_dict.iteritems():
        module_dict_state[is_document] = _APDEXDateDictAsJSONState(date_dict)
    for attribute_id in ('no_module', 'site_search'):
      result[attribute_id] = _APDEXDateDictAsJSONState(getattr(self,
        attribute_id))
    return result

  def accumulateFrom(self, other):
    super(ERP5SiteStats, self).accumulateFrom(other)
    module = self.module
    for module_id, other_module_dict in other.module.iteritems():
      module_dict = module[module_id]
      for is_document, other_date_dict in other_module_dict.iteritems():
        date_dict = module_dict[is_document]
        for value_date, apdex in other_date_dict.iteritems():
          date_dict[value_date].accumulateFrom(apdex)
    for attribute_id in ('no_module', 'site_search'):
      attribute = getattr(self, attribute_id)
      for value_date, apdex in getattr(other, attribute_id).iteritems():
        attribute[value_date].accumulateFrom(apdex)

DURATION_US_FORMAT = '%D'
DURATION_S_FORMAT = '%T'

server_name_group_dict = {
  '%v': lambda x: x.group('servername') + '/',
  '%V': lambda x: x.group('canonical_servername') + '/',
}

logformat_dict = {
  '%h': r'(?P<host>[^ ]*)',
  '%l': r'(?P<ident>[^ ]*)',
  '%u': r'(?P<user>[^ ]*)',
  '%t': r'\[(?P<timestamp>[^\]]*)\]',
  '%r': r'(?P<request>[^"]*)', # XXX: expected to be enclosed in ". See also REQUEST_PATTERN
  '%>s': r'(?P<status>[0-9]*?)',
  '%O': r'(?P<size>[0-9-]*?)',
  '%{Referer}i': r'(?P<referer>[^"]*)', # XXX: expected to be enclosed in "
  '%{User-Agent}i': r'(?P<agent>[^"]*)', # XXX: expected to be enclosed in "
  DURATION_US_FORMAT: r'(?P<duration>[0-9]*)',
  DURATION_S_FORMAT: r'(?P<duration_s>[0-9]*)',
  '%%': r'%',
  '%v': r'(?P<servername>[^ ]*)',
  '%V': r'(?P<canonical_servername>[^ ]*)',
  # TODO: add more formats
}

# Expensive, but more robust, variants
expensive_logformat_dict = {
  '%r': r'(?P<request>(\\.|[^\\"])*)',
  '%{Referer}i': r'(?P<referer>(\\.|[^\\"])*)',
  '%{User-Agent}i': r'(?P<agent>(\\.|[^\\"])*)',
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
    action = base_action = self.__argument_to_aggregator[option_string]
    site_list, site_caption_dict = getattr(namespace, self.dest)
    next_value = iter(values).next
    while True:
      try:
        value = next_value()
      except StopIteration:
        break
      if value in site_caption_dict:
        raise ValueError('Duplicate base: %r' % value)
      if action is not None and value[0] == '+':
        caption = value[1:]
        try:
          value = next_value()
        except StopIteration:
          raise ValueError('No base follows caption %r' % value)
      else:
        caption = value
      site_caption_dict[value] = caption
      caption = None
      match = re.compile(value).match
      if base_action is not None:
        match_suffix = re.compile(value + '(?P<suffix>.*)').match
        action = partial(base_action,
          suffix=lambda x: match_suffix(x).group('suffix'))
      site_list.append((value, match, action))

class ShlexArgumentParser(argparse.ArgumentParser):
  """
  Two objectives in this class:
  - use shlex to split config files
  - when recursively including files, do it from referer's path instead of
    current working directory, to facilitate relative inclusion.
  """
  # XXX: I whould like to be able to hook inside _read_args_from_files, but
  # it would be dirtier. Instead, declare a private method doing similar
  # replacement before handing args to original parse_known_args.
  def __read_args_from_files(self, args, cwd):
    new_args = []
    append = new_args.append
    extend = new_args.extend
    for arg in args:
      if arg[:1] in self.fromfile_prefix_chars:
        filepath = arg[1:]
        new_cwd = os.path.normpath(os.path.join(
          cwd,
          os.path.dirname(filepath),
        ))
        try:
          with open(os.path.join(new_cwd, os.path.basename(filepath))
              ) as in_file:
            extend(self.__read_args_from_files(
              shlex.split(in_file.read(), comments=True),
              new_cwd,
            ))
        except IOError, exc:
          self.error(str(exc))
      else:
        append(arg)
    return new_args

  def parse_known_args(self, args=None, namespace=None):
    if args is None:
      args = sys.argv[1:]
    else:
      args = list(args)
    args = self.__read_args_from_files(args, os.getcwd())
    return super(ShlexArgumentParser, self).parse_known_args(args=args,
      namespace=namespace)

def _asMonthString(timestamp):
  dt, _ = timestamp.split(' ')
  _, month, year = dt.split(':', 1)[0].split('/')
  return '%s/%02i' % (year, MONTH_VALUE_DICT[month])

_month_offset_cache = {}

def _asWeekString(timestamp):
  dt, _ = timestamp.split(' ')
  day, month, year = dt.split(':', 1)[0].split('/')
  year = int(year)
  month = MONTH_VALUE_DICT[month]
  day = int(day)
  key = (year, month)
  try:
    offset = _month_offset_cache[key]
  except KeyError:
    # Substract 1 to exclude first day of month, and 1 to prepare for next
    # operation (avoid substracting on each run).
    offset = date(year, month, 1).timetuple().tm_yday - 2
    _month_offset_cache[key] = offset
  day_of_year = day + offset
  day -= day_of_year - (day_of_year / 7 * 7)
  if day < 1:
    month -= 1
    day += calendar.monthrange(year, month)[1]
    assert day > 0 and month > 0, (timestamp, year, month, day)
  return '%04i/%02i/%02i' % (year, month, day)

def _weekStringAsQuarterString(timestamp):
  year, month, _ = timestamp.split('/')
  return '%s/%02i' % (year, (int(month) - 1) / 3 * 3 + 1)

def _roundWeek(dt):
  day_of_year = dt.timetuple().tm_yday
  return dt - timedelta(day_of_year - ((day_of_year - 1) / 7 * 7 + 1))

def _getWeekCoefficient(dt):
  if dt.month != 12:
    return 1
  # 32 = 31 days of December + 1 day so YYYY/12/31 is still 1 day of measure,
  # and return value is 7.
  return max(1, 7. / (32 - dt.day))

def _asDayString(timestamp):
  dt, _ = timestamp.split(' ')
  day, month, year = dt.split(':', 1)[0].split('/')
  return '%s/%02i/%s' % (year, MONTH_VALUE_DICT[month], day)

def _as6HourString(timestamp):
  dt, _ = timestamp.split(' ')
  dt_date, hour, _ = dt.split(':', 2)
  day, month, year = dt_date.split('/')
  return '%s/%02i/%s %02i' % (year, MONTH_VALUE_DICT[month], day,
    int(hour) / 6 * 6)

def _round6Hour(dt):
  return dt.replace(hour=dt.hour / 6 * 6)

def _hourAsWeekString(timestamp):
  dt = datetime.strptime(timestamp, '%Y/%m/%d %H')
  return (dt - timedelta(dt.weekday())).date().strftime('%Y/%m/%d')

def _asHourString(timestamp):
  dt, _ = timestamp.split(' ')
  dt_date, hour, _ = dt.split(':', 2)
  day, month, year = dt_date.split('/')
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
# - round a datetime.datetime instance so once represented using given format
#   string it is a valid graph-granularity date for period
# - coefficient to apply to hit count for given (graph granularity)
#   datetime.datetime. Most useful in case of "7 days", as last month's week
#   may be a single day, causing graph to display a value up to 7 times lower
#   than what it should be.
period_parser = {
  'year': (
    _asMonthString,
    lambda x: x.split('/', 1)[0],
    'month',
    '%Y/%m',
    # Longest month: 31 days
    timedelta(31),
    lambda x: x,
    # Error margin without correction: 3/31 = 10%
    lambda x: 31. / calendar.monthrange(x.year, x.month)[1],
  ),
  'quarter': (
    _asWeekString,
    _weekStringAsQuarterString,
    # Note: Not calendar weeks, but chunks of 7 days starting on first year's
    # day. Cheaper to compute than locating first sunday/monday of the year.
    '7 days',
    '%Y/%m/%d',
    timedelta(7),
    _roundWeek,
    # Error margin without correction: (366 % 7 = 2) 2/7 = 29%
    _getWeekCoefficient,
  ),
  'month': (
    _asDayString,
    lambda x: '/'.join(x.split('/', 2)[:2]),
    'day',
    '%Y/%m/%d',
    # Longest day: 24 hours + 1h DST (never more ?)
    timedelta(seconds=3600 * 25),
    lambda x: x,
    # Error margin without correction: (DST) 1/24 = 4%
    lambda x: 1,
  ),
  'week': (
    _as6HourString,
    _hourAsWeekString,
    '6 hours',
    '%Y/%m/%d %H',
    timedelta(seconds=3600 * 6),
    _round6Hour,
    # Error margin without correction: (DST) 1/6 = 17%
    lambda x: 1,
  ),
  'day': (
    _asHourString,
    lambda x: x.split(' ')[0],
    'hour',
    '%Y/%m/%d %H',
    # Longest hour: 60 * 60 seconds + 1 leap second.
    timedelta(seconds=3601),
    lambda x: x,
    # Error margin without correction: (leap) 1/3600 = .03%
    lambda x: 1,
  ),
}

unquoteToHtml = lambda x, encoding: escape(unquote(x).decode(encoding,
  'replace'))

apdex_y_scale_dict = {
  'linear': None,
  'log': 'log100To0',
}

def asHTML(out, encoding, per_site, args, default_site, period_parameter_dict,
    stats, site_caption_dict):
  period = period_parameter_dict['period']
  decimator = period_parameter_dict['decimator']
  date_format = period_parameter_dict['date_format']
  placeholder_delta = period_parameter_dict['placeholder_delta']
  graph_period = period_parameter_dict['graph_period']
  graph_coefficient = period_parameter_dict['graph_coefficient']
  hit_y_max = args.fixed_yrange
  if hit_y_max is not None:
    apdex_y_min = hit_y_min = 0
    if hit_y_max < 0:
      hit_y_max = None
  else:
    apdex_y_min = hit_y_min = None
  out.write('<!DOCTYPE html>\n<html><head><meta charset="%s">'
    '<title>Stats</title>' % encoding)
  js_path = args.js
  js_embed = js_path is None or args.js_embed
  if js_embed:
    out.write('<style>')
    out.write(getResource('apachedex.css'))
    out.write('</style>')
  else:
    out.write('<link rel="stylesheet" type="text/css" '
      'href="%s/apachedex.css"/>' % js_path)
  for script in ('jquery.js', 'jquery.flot.js', 'jquery.flot.time.js',
      'jquery.flot.axislabels.js', 'jquery-ui.js', 'apachedex.js'):
    if js_embed:
      out.write('<script type="text/javascript">//<![CDATA[\n')
      out.write(getResource(script))
      out.write('\n//]]></script>')
    else:
      out.write('<script type="text/javascript" src="%s/%s"></script>' % (
        js_path, script))
  apdex_y_scale = apdex_y_scale_dict[args.apdex_yscale]
  out.write('</head><body><h1>Overall</h1>')
  site_list = list(enumerate(sorted(per_site.iteritems(),
    key=lambda x: site_caption_dict[x[0]])))
  html_site_caption_dict = {}
  for i, (site_id, _) in site_list:
    html_site_caption_dict[site_id] = unquoteToHtml(site_caption_dict[site_id],
      encoding)
  if len(per_site) > 1:
    out.write('<h2>Index</h2><ol>')
    for i, (site_id, _) in site_list:
      out.write('<li><a href="#%s" title="%s">%s</a></li>' % (i,
        escape(repr(site_id), quote=True), html_site_caption_dict[site_id]))
    out.write('</ol>')
  out.write('<h2>Parameters</h2><table class="stats">')
  for caption, value in (
        ('apdex threshold', '%.2fs' % args.apdex),
        ('period', args.period or (period + ' (auto)')),
      ):
    out.write('<tr><th class="text">%s</th><td>%s</td></tr>' % (
      caption, value))
  out.write('</table><h2>Hits per period</h2><table class="stats">'
    '<tr><th>date</th><th>hits</th></tr>')
  hit_per_day = defaultdict(int)
  x_min = LARGER_THAN_INTEGER_STR
  x_max = None
  for site_data in per_site.itervalues():
    apdex_data_list = site_data.getApdexData()
    if apdex_data_list:
      x_min = min(x_min, apdex_data_list[0][0])
      x_max = max(x_max, apdex_data_list[-1][0])
      for hit_date, _, hit in apdex_data_list:
        hit_per_day[decimator(hit_date)] += hit
  if x_min == LARGER_THAN_INTEGER_STR:
    x_min = None
  for hit_date, hit in sorted(hit_per_day.iteritems(), key=ITEMGETTER0):
    out.write('<tr><td>%s</td><td>%s</td></tr>' % (hit_date, hit))
  out.write('</table>')
  for i, (site_id, data) in site_list:
    out.write('<h1 id="%s" title="%s">%s</h1>' % (i, escape(repr(site_id),
      quote=True), html_site_caption_dict[site_id]))
    apdex_data = data.getApdexData()
    if apdex_data:
      out.write(
        graphPair(
          prepareDataForGraph(
            apdex_data,
            date_format,
            placeholder_delta,
            graph_coefficient,
            x_min=x_min,
            x_max=x_max,
          ),
          date_format,
          graph_period,
          apdex_y_min=apdex_y_min,
          hit_y_min=hit_y_min,
          hit_y_max=hit_y_max,
          apdex_y_scale=apdex_y_scale,
        )
      )
    out.write(data.asHTML(date_format, placeholder_delta, graph_period,
      graph_coefficient, encoding, decimator,
      x_min=x_min, x_max=x_max,
      apdex_y_min=apdex_y_min, hit_y_min=hit_y_min, hit_y_max=hit_y_max,
      apdex_y_scale=apdex_y_scale,
    ))
  end_stat_time = time.time()
  if args.stats:
    out.write('<h1>Parsing stats</h1><table class="stats">')
    buildno, builddate = platform.python_build()
    end_parsing_time = stats['end_parsing_time']
    parsing_time = end_parsing_time - stats['parsing_start_time']
    all_lines = stats['all_lines']
    for caption, value in (
          ('Execution date', datetime.now().isoformat()),
          ('Interpreter', '%s %s build %s (%s)' % (
            platform.python_implementation(),
            platform.python_version(),
            buildno,
            builddate,
          )),
          ('State file count', stats['state_file_count']),
          ('State loading time', timedelta(seconds=stats['parsing_start_time']
            - stats['loading_start_time'])),
          ('File count', stats['file_count']),
          ('Lines', all_lines),
          ('... malformed', stats['malformed_lines']),
          ('... URL-less', stats['no_url_lines']),
          ('... skipped (URL)', stats['skipped_lines']),
          ('... skipped (user agent)', stats['skipped_user_agent']),
          ('Parsing time', timedelta(seconds=parsing_time)),
          ('Parsing rate', '%i line/s' % (all_lines / parsing_time)),
          ('Rendering time', timedelta(seconds=(
            end_stat_time - end_parsing_time))),
        ):
      out.write('<tr><th class="text">%s</th><td>%s</td></tr>' % (
        caption, value))
    out.write('</table>')
  out.write('</body></html>')

def asJSON(out, encoding, per_site, *_):
  json.dump([(x, y.asJSONState()) for x, y in per_site.iteritems()], out,
    encoding='ascii')

format_generator = {
  'html': (asHTML, 'utf-8'),
  'json': (asJSON, 'ascii'),
}

# XXX: monkey-patching json module to emit strings instead of unicode objects.
# Because strings are faster, (30% overall performance hit moving to unicode
# objects), and only ASCII is expected (urlencoded is ASCII).
# Subclassing JSONDecoder is not enough as object parser uses scanstring
# directly.
original_scanstring = json.decoder.scanstring
def _scanstring(*args, **kw):
  string, end = original_scanstring(*args, **kw)
  return string.encode('ascii'), end
json.decoder.scanstring = _scanstring

def main():
  global abs_file_container
  parser = ShlexArgumentParser(description='Compute Apdex out of '
    'apache-style log files', fromfile_prefix_chars='@')
  parser.add_argument('logfile', nargs='*',
    help='Log files to process. Use - for stdin.')
  parser.add_argument('-l', '--logformat',
    default='%h %l %u %t "%r" %>s %O "%{Referer}i" "%{User-Agent}i" %D',
    help='Apache LogFormat used to generate provided logs. '
      'Default: %(default)r')
  parser.add_argument('-o', '--out', default='-',
    help='Filename to write output to. Use - for stdout. Default: %(default)s')
  parser.add_argument('-q', '--quiet', action='store_true',
    help='Suppress warnings about malformed lines.')
  parser.add_argument('-Q', '--no-progress', action='store_true',
    help='Suppress progress indication (file being parsed, lines counter). '
      'Does not imply -q.')
  parser.add_argument('--state-file', nargs='+', default=[],
    help='Use given JSON files as initial state. Use - for stdin.')

  group = parser.add_argument_group('generated content (all formats)')
  group.add_argument('-a', '--apdex', default=1.0, type=float,
    help='First threshold for Apdex computation, in seconds. '
      'Default: %(default).2fs')
  group.add_argument('-e', '--error-detail', action='store_true',
    help='Include detailed report (url & referers) for error statuses.')
  group.add_argument('-f', '--format', choices=format_generator,
    default='html', help='Format in which output should be generated.')
  group.add_argument('-p', '--period', choices=period_parser,
      help='Periodicity of sampling buckets. Default: (decide from data).')

  group = parser.add_argument_group('generated content (html)')
  group.add_argument('-s', '--stats', action='store_true',
    help='Enable parsing stats (time spent parsing input, time spent '
      'generating output, ...)')
  group.add_argument('--js', default=abs_file_container,
    help='Folder containing needed js files. Default: %(default)s')
  group.add_argument('--js-embed', action='store_true',
    help='Embed js files instead of linking to them.')
  group.add_argument('--fixed-yrange', nargs='?', type=int, const=-1,
    help='Fix graph vertical range: 0-100%% for apdex, 0-value for hits. '
      'Negative value means hit max is adapted to data (used when this '
      'argument is provided without value).')
  group.add_argument('--apdex-yscale', default='linear',
    choices=apdex_y_scale_dict,
    help='apdex graph ordinate scale. Default: %(default)s')

  group = parser.add_argument_group('site matching', 'Earlier arguments take '
    'precedence. Arguments are Python regexes, matching urlencoded strings.'
    'Regex matches can be named by providing a "+"-prefixed string before '
    'regex.')
  group.add_argument('-d', '--default',
    help='Caption for lines matching no prefix, or skip them if not provided.')
  group.add_argument('--base', dest='path', default=([], {}), nargs='+',
    action=AggregateSiteUrl,
    help='Title (optional) and regexes matching parts of a site.')
  group.add_argument('--erp5-base', dest='path', nargs='+',
    action=AggregateSiteUrl,
    help='Similar to --base, but with specialised statistics. Ex: '
    '"/erp5(/|$|\?)"')
  group.add_argument('--skip-base', dest='path', nargs='+',
    action=AggregateSiteUrl,
    help='Absolute base url(s) to ignore.')
  group.add_argument('--match-servername', choices=server_name_group_dict,
    help='Prefix URL with (canonical) server name.')

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
  if args.match_servername is not None and \
      args.match_servername not in args.logformat:
    print >> sys.stderr, '--match-servername %s requested, but missing ' \
      'from logformat.' % args.match_servername
    sys.exit(1)
  get_url_prefix = server_name_group_dict.get(args.match_servername,
    lambda _: '')
  line_regex = ''
  expensive_line_regex = ''
  try:
    n = iter(args.logformat).next
    while True:
      key = None
      expensive_char = char = n()
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
        expensive_char = expensive_logformat_dict.get(key, char)
      line_regex += char
      expensive_line_regex += expensive_char
  except StopIteration:
    assert not key, key
  matchline = re.compile(line_regex).match
  expensive_matchline = re.compile(expensive_line_regex).match
  matchrequest = REQUEST_PATTERN.match
  if args.period is None:
    next_period_data = ((x, y[4] * AUTO_PERIOD_COEF) for (x, y) in
      sorted(period_parser.iteritems(), key=lambda x: x[1][4])).next
    period, to_next_period = next_period_data()
    original_period = period
    earliest_date = latest_date = None
    def getNextPeriod():
      # datetime is slow (compared to string operations), but not many choices
      return (datetime.strptime(earliest_date, date_format) + to_next_period
        ).strftime(date_format)
    def rescale(x):
      result = round_date(datetime.strptime(x, old_date_format)).strftime(date_format)
      return result
  else:
    to_next_period = None
    period = args.period
  asDate, decimator, graph_period, date_format, placeholder_delta, \
    round_date, graph_coefficient = period_parser[period]
  site_list, site_caption_dict = args.path
  default_site = args.default
  if default_site is None:
    default_action = None
    if not [None for _, _, x in site_list if x is not None]:
      print >> sys.stderr, 'None of --default, --erp5-base and --base were ' \
        'specified, nothing to do.'
      sys.exit(1)
  else:
    default_action = partial(GenericSiteStats, suffix=lambda x: x)
    site_caption_dict[None] = default_site
  infile_list = args.logfile
  quiet = args.quiet
  threshold = args.apdex
  error_detail = args.error_detail
  file_count = len(infile_list)
  per_site = {}
  if '-' in args.state_file and '-' in infile_list:
    print >> sys.stderr, 'stdin cannot be used both as log and state input.'
    sys.exit(1)
  loading_start_time = time.time()
  for state_file_name in args.state_file:
    print >> sys.stderr, 'Loading', state_file_name, '...',
    if state_file_name == '-':
      state_file = sys.stdin
    else:
      state_file = open(state_file_name)
    with state_file:
      load_start = time.time()
      state = json.load(state_file, encoding='ascii')
      for url, site_state in state:
        if url is None:
          site = None
          action = default_action
        else:
          for site, prefix_match, action in site_list:
            if site == url:
              break
          else:
            site = None
            action = default_action
        if action is None:
          print >> sys.stderr, 'Info: no prefix match %r, stats skipped' % url
          continue
        site_stats = action.func.fromJSONState(site_state,
          getDuration, action.keywords['suffix'])
        if site in per_site:
          per_site[site].accumulateFrom(site_stats)
        else:
          per_site[site] = site_stats
      print >> sys.stderr, 'done (%s)' % timedelta(seconds=time.time()
        - load_start)
  skip_user_agent = list(itertools.chain(*args.skip_user_agent))
  malformed_lines = 0
  skipped_lines = 0
  no_url_lines = 0
  all_lines = 0
  skipped_user_agent = 0
  show_progress = not args.no_progress
  parsing_start_time = time.time()
  for fileno, filename in enumerate(infile_list, 1):
    if show_progress:
      print >> sys.stderr, 'Processing %s [%i/%i]' % (
        filename, fileno, file_count)
    if filename == '-':
      logfile = sys.stdin
    else:
      for opener, exc in FILE_OPENER_LIST:
        logfile = opener(filename)
        try:
          logfile.readline()
        except exc:
          continue
        else:
          logfile.seek(0)
          break
      else:
        logfile = open(filename)
    lineno = 0
    for lineno, line in enumerate(logfile, 1):
      if show_progress and lineno % 5000 == 0:
        print >> sys.stderr, lineno, '\r',
      match = matchline(line)
      if match is None:
        match = expensive_matchline(line)
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
      url = get_url_prefix(match) + url
      for site, prefix_match, action in site_list:
        if prefix_match(url) is not None:
          break
      else:
        site = None
        action = default_action
      if action is None:
        skipped_lines += 1
        continue
      hit_date = asDate(match.group('timestamp'))
      if to_next_period is not None:
        if hit_date > latest_date: # '' > None is True
          latest_date = hit_date
        if hit_date < earliest_date or earliest_date is None:
          earliest_date = hit_date
          next_period = getNextPeriod()
        try:
          while latest_date > next_period:
            period, to_next_period = next_period_data()
            next_period = getNextPeriod()
        except StopIteration:
          to_next_period = None
        if original_period != period:
          original_period = period
          if show_progress:
            print >> sys.stderr, 'Increasing period to', period, '...',
          old_date_format = date_format
          asDate, decimator, graph_period, date_format, placeholder_delta, \
            round_date, graph_coefficient = period_parser[period]
          latest_date = rescale(latest_date)
          earliest_date = rescale(earliest_date)
          period_increase_start = time.time()
          for site_data in per_site.itervalues():
            site_data.rescale(rescale, getDuration)
          if show_progress:
            print >> sys.stderr, 'done (%s)' % timedelta(seconds=time.time()
              - period_increase_start)
          hit_date = asDate(match.group('timestamp'))
      try:
        site_data = per_site[site]
      except KeyError:
        site_data = per_site[site] = action(threshold, getDuration,
          error_detail=error_detail)
      try:
        site_data.accumulate(match, url_match, hit_date)
      except Exception:
        if not quiet:
          print >> sys.stderr, 'Error analysing line at %s:%i: %r' % (filename,
            lineno, line)
          print >> sys.stderr, traceback.format_exc()
    all_lines += lineno
    if show_progress:
      print >> sys.stderr, lineno
  end_parsing_time = time.time()
  generator, out_encoding = format_generator[args.format]
  if args.out == '-':
    out = sys.stdout
  else:
    out = codecs.open(args.out, 'w', encoding=out_encoding)
  with out:
    generator(out, out_encoding, per_site, args, default_site, {
        'period': period,
        'decimator': decimator,
        'date_format': date_format,
        'placeholder_delta': placeholder_delta,
        'graph_period': graph_period,
        'graph_coefficient': graph_coefficient,
      }, {
        'state_file_count': len(args.state_file),
        'loading_start_time': loading_start_time,
        'parsing_start_time': parsing_start_time,
        'end_parsing_time': end_parsing_time,
        'file_count': file_count,
        'all_lines': all_lines,
        'malformed_lines': malformed_lines,
        'no_url_lines': no_url_lines,
        'skipped_lines': skipped_lines,
        'skipped_user_agent': skipped_user_agent,
      },
      site_caption_dict,
    )

if __name__ == '__main__':
  main()
