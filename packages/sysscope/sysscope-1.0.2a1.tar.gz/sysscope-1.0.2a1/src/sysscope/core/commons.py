# -*- coding: utf-8 -*-
#
#  This file is part of sysscope.
#
#  sysscope - Tool for visual representation of RRDtool's Round Robin Databases.
#
#  Project: https://www.codetrax.org/projects/sysscope
#
#  Copyright 2008 George Notaras <gnot [at] g-loaded.eu>, CodeTRAX.org
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import string
import subprocess

from sysscope.core.exceptions import RrdToolError


def get_variable_name_pool():
    pool = []
    for m in string.lowercase:
        for n in string.lowercase:
            pool.append("%s%s" % (m, n))
    return pool


def canonical_name(name):
    """
    - Removes disallowed characters (punctuation)
    - Replaces spaces with dashes
    - Strip dashes from start and end of string
    - Converts to lowercase
    """
    def allowed_char(c):
        if c not in string.punctuation:
            return True
    name = filter(allowed_char, name)
    name = name.replace(' ', '-')
    name = name.strip('-')
    return name.lower()


def get_graph_image_data(options):
    args = ['rrdtool', 'graph', '-']
    args.extend(options)
    #import pprint
    #pprint.pprint (args)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    image_data = p.stdout.read()
    if not image_data:
        import pprint
        rrdtool_params = pprint.pformat(args)
        raise RrdToolError(rrdtool_params)
    errors = p.stdout.read()
    if errors:
        raise RrdToolError(errors)
    #for line in p.stderr:
    #    #print line
    #    continue    # TODO: find way to display errors: mod_wsgi by default restricts printing to stdout
    return image_data
