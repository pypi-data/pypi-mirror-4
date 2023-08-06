# Name:      setup.py
# Purpose:   
# Copyright: 2011: Database Associates Ltd.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#    See the License for the specific language governing permissions and
#    limitations under the License.

#-----------------------------------------------------------------------

from ConfigParser import RawConfigParser
from distutils.core import setup

#-----------------------------------------------------------------------

def multiline(value, multi):
    if multi != 's':
        value = [v for v in
                 [v.strip() for v in value.split('\n')]
                 if v != '']
    return value

def make_dir(data_list):
    new_value = {}
    for item in data_list:
        key, value = item.split('=')
        key = key.strip()
        value = value.strip()
        if key not in new_value:
            new_value[key] = []
        new_value[key].append(value)
    return new_value
    
#-----------------------------------------------------------------------

# Read the setup2.cfg file
parser = RawConfigParser()
parser.read('setup2.cfg')

name_map = {
    'name': ('name', 's'),
    'version': ('version', 's'),
    'platform': ('platform', 's'),
    'supported_platform': ('supported_platform', 'm'),
    'author': ('author', 's'),
    'author_email': ('author_email', 's'),
    'maintainer': ('maintainer', 's'),
    'maintainer_email': ('maintainer_email', 's'),
    'summary': ('description', 's'),
    'description': ('long_description', 's'),
    'description_file': ('description_file', 's'),
    'keywords': ('keywords', 's'),
    'home_page': ('url', 's'),
    'download_url': ('download_url', 's'),
    'license': ('license', 's'),
    'classifier': ('classifiers', 'm'),
    'requires_dist': ('requires', 'm'),
    'provides_dist': ('provides', 'm'),
    'obsoletes_dist': ('obsoletes', 'm'),
    'requires_python': ('requires_python', 'm'),
    'requires_externals': ('requires_externals', 'm'),
    'project_url': ('project_url', 'm'),
    'packages_root': ('packages_root', 's'),
    'modules': ('modules', 'm'),
    'packages': ('packages', 'm'),
    'scripts': ('scripts', 'm'),
    'extra_files': ('extra_files', 'm'),
    'package_data': ('package_data', 'm'),
    'data_files': ('data_files', 'm'),
    }


# Expecting some or all of:
# 'name'
# 'version'
# 'author'
# 'author_email'
# 'maintainer'
# 'maintainer_email'
# 'url'
# 'description'
# 'long_description'
# 'download_url'
# 'classifiers'
# 'platforms'
# 'license'
# 'packages'
# 'package_data'
# 'requires'
# 'scripts'
data = {}


if 'metadata' in parser.sections():
    for key, value in parser.items('metadata'):
        key = key.replace('-', '_')
        item = name_map[key]
        value = multiline(value, item[1])
        data[item[0]] = value
if 'files' in parser.sections():
    for key, value in parser.items('files'):
        key = key.replace('-', '_')
        item = name_map[key]
        value = multiline(value, item[1])
        data[item[0]] = value

if 'package_data' in data:
    # convert a list to a dictionary of lists
    data['package_data'] = make_dir(data['package_data'])

if 'description_file' in data:
    fp = open(data['description_file'], 'r')
    try:
        data['long_description'] = fp.read()
    finally:
        fp.close()
    del data['description_file']
#

setup(**data)

#-----------------------------------------------------------------------
