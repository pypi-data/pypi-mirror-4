# Copyright 2013 Fredrik Brannbacka
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json

plugins_dirs = [os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins")]
if 'LOGWORM_WORMS_DIR' in os.environ.keys():
    plugins_dirs.append(os.environ['LOGWORM_WORMS_DIR'].split(':'))

WORMS = {}
for plugins_dir in plugins_dirs:
    if os.path.exists(plugins_dir):
        for plugin_file in os.listdir(plugins_dir):
            if plugin_file.endswith('.json'):
                worm_data = json.load(open(os.path.join(plugins_dir, plugin_file)))
                WORMS[worm_data['name']] = worm_data['parsers']


def registerWorm_from_dict(worm_dict):
    WORMS[worm_dict['name']] = worm_dict['parsers']


def registerWorm_from_file(worm_file):
    worm_data = json.load(open(worm_file))
    WORMS[worm_data['name']] = worm_data['parsers']

from core import LogWorm

__all__ = ["LogWorm", "WORMS"]
