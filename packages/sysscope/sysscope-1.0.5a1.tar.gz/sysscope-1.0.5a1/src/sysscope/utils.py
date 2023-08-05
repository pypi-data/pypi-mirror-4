# -*- coding: utf-8 -*-
#
#  This file is part of sysscope.
#
#  sysscope - Tool for visual representation of RRDtool's Round Robin Databases.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/sysscope
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/sysscope
#
#  Copyright 2012 George Notaras <gnot [at] g-loaded.eu>
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

import time


#
# Time related functions
#


TIME_FRAMES_ORDERED = ['S', 'M', 'H', 'd', 'w', 'm', 'y']
TIME_FRAME_POOL = {
    'S' : ('%s' % (1),            'Second', 'per second'),
    'M' : ('%s' % (60),           'Minute', 'per mnute'),
    'H' : ('%s' % (60*60),        'Hour',   'hourly'),
    'd' : ('%s' % (60*60*24),     'Day',    'daily'),
    'w' : ('%s' % (60*60*24*7),   'Week',   'weekly'),
    'm' : ('%s' % (60*60*24*30),  'Month',  'monthly'),
    'y' : ('%s' % (60*60*24*365), 'Year',   'yearly'),
}



def resolve_time(t, make_absolute=False):
    """
    Might be all supported formats
    negative notation means "relative to now"
    """
    time_current = int(time.time())
    
    t_is_relative_to_now = False
    if t.startswith('-'):
        t_is_relative_to_now = True
    
    # Strip the minus sign (if any).
    # This is not required since "t_is_relative_to_now" has been set
    t = t.lstrip('-')
    
    # If a special notation has been used, for instance: "12d",
    # resolve the time to a timestamp
    notation = t[-1]
    if notation in TIME_FRAME_POOL.keys():
        multiplier = t[:-1] or 1
        t = int(multiplier) * int(TIME_FRAME_POOL[notation][0])

    # If the time is relative to the current time, convert it to absolute time,
    # only if "make_absolute" has been set to True.
    if make_absolute:
        if t_is_relative_to_now:
            t = int(time_current) - int(t)
    
    # timestamp
    try:
        return int(t)
    except ValueError:
        raise Exception('Invalid time: %s' % repr(t))


    
def get_graph_times(start, timeframe):
    """
    Helper function.
    
    Given times in the query args might be all supported formats.
    Negative notation means "relative to now"
    
    Returns 3 integers :
        - t_start (timestamp)
        - t_end (timestamp)
        - t_frame (difference between the other two)
    
    t_start and t_end are ansolute times. This means they are timestamps
    and not times relative to the current time.
    
    """

    t_start = resolve_time(start, make_absolute=True)
    t_frame = resolve_time(timeframe, make_absolute=False)
    t_end = t_start + t_frame
    
    return t_start, t_end, t_frame


def get_section_report_title(section_obj, start, timeframe):
    """
    section: Section object
    """
    # If a special notation has been used (eg 12H), then we only need the last
    # character in order to determine which entry of the TIME_FRAME_POOL we need
    try:
        time_frame_data = TIME_FRAME_POOL[timeframe[-1]]
    except KeyError:
        try:
            return '%s timely graphs (%d seconds)' % (section_obj.name, int(timeframe))
        except ValueError:
            raise Exception('Invalid timeframe: %s' % repr(timeframe))
    else:
        return '%s %s graphs' % (section_obj.name, time_frame_data[2])

