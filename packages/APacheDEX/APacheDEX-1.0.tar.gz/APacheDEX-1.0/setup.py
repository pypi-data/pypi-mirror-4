from os.path import join, exists
from setuptools import setup, find_packages
import hashlib
import sys
import urllib

FLOT_SHA = 'aefe4e729b2d14efe6e8c0db359cb0e9aa6aae52'
FLOT_AXISLABELS_SHA = '80453cd7fb8a9cad084cf6b581034ada3339dbf8'
JQUERY_VERSION = '1.9.1'

DEPS = {
  'jquery.flot.js': (
    'http://raw.github.com/flot/flot/%s/jquery.flot.js' % FLOT_SHA,
    '7b599c575f19c33bf0d93a6bbac3af02',
  ),
  'jquery.flot.time.js': (
    'http://raw.github.com/flot/flot/%s/jquery.flot.time.js' % FLOT_SHA,
    'c0aec1608bf2fbb79f24d1905673e2c3',
  ),
  'jquery.flot.axislabels.js': (
    'http://raw.github.com/markrcote/flot-axislabels/%s/'
      'jquery.flot.axislabels.js' % FLOT_AXISLABELS_SHA,
    'a8526e0c1ed3b5cbc1a6b3ebb22bf334',
  ),
  'jquery.js': (
    'http://code.jquery.com/jquery-%s.min.js' % JQUERY_VERSION,
    '397754ba49e9e0cf4e7c190da78dda05',
  ),
}

def download(url, filename, hexdigest):
  filename = join('apachedex', filename)
  if not exists(filename):
    urllib.urlretrieve(url, filename)
  if hashlib.md5(open(filename).read()).hexdigest() != hexdigest:
    raise EnvironmentError('Checksum mismatch downloading %r' % filename)

for filename, (url, hexdigest) in DEPS.items():
  download(url, filename, hexdigest)

# XXX: turn this into a setuptool command ?
if sys.argv[1:] == ['deps']:
  sys.exit(0)

description = open('README').read()

setup(
  name='APacheDEX',
  version='1.0',
  description=(x for x in description.splitlines() if x.strip()).next(),
  long_description=".. contents::\n\n" + description,
  author='Vincent Pelletier',
  author_email='vincent@nexedi.com',
  url='http://git.erp5.org/gitweb/apachedex.git',
  license='GPL 2+',
  platforms=['any'],
  classifiers=[
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: System :: Logging',
    'Topic :: Text Processing :: Filters',
    'Topic :: Text Processing :: Markup :: HTML',
  ],
  packages=find_packages(),
  entry_points = {
    'console_scripts': [
      'apachedex=apachedex:main',
    ],
  },
  package_data={
    'apachedex': DEPS.keys(),
  },
  zip_safe=True,
)
