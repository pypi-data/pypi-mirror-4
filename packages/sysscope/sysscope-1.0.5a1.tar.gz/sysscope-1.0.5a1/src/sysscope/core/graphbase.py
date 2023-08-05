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

import rrdtool
import datetime

from sysscope.core.commons import canonical_name


class GraphOptionError(Exception):
    pass


class Graph:

    # Options without --
    NON_DASH_OPTIONS = ('DEF:', 'VDEF', 'CDEF', 'GPRINT', 'COMMENT', 'HRULE', 'VRULE')

    def __init__(self, title):

        self.Name = title
        self.CanonicalName = canonical_name(title)
        self.Template = None
        self.LegendFormat = '%9.3lf'
        self.HasLegendColumns = False

        self.RRDGraphOptions = [
            '--imgformat', 'PNG',
            '--watermark', 'Produced with sysscope',
            '--start', 'end-1d',
            '--end', 'now',
            ]

        self.extend( ['--title', title] )    # Add the title to the graph options

    def append(self, option):
        self.RRDGraphOptions.append(option)

    def extend(self, option_list):
        self.RRDGraphOptions.extend(option_list)

    def merge_options(self, user_prefs):
        """
        This is really nasty, but does what it was written for. -- Needs rewrite
        """
        # TODO
        skip_next = False
        for n, option in enumerate(user_prefs):
            if skip_next:
                skip_next = False
                continue
            elif not option.startswith('--'):
                continue
            elif option in self.RRDGraphOptions:    # If the option exists in the RRDGraphOptions (main graph options)
                option_index = self.RRDGraphOptions.index(option)    # Get the the index of the option in the RRDGraphOptions list
                pv = self.RRDGraphOptions[option_index + 1]    # possible value: This is the next item in the RRDGraphOptions list
                if not pv.startswith('--') and pv[:3] not in self.NON_DASH_OPTIONS:    # if the next item (pv) does not start with '--' and
                                                    # is not a DEF/VDEF/CDEF argument, then 'pv' is possibly the value
                                                    # of 'option'. So we need to substitute the respective item in
                                                    # the RRDGraphOptions list with the one from the user_prefs
                    if user_prefs[n+1].startswith('--') or user_prefs[n+1][:3] in self.NON_DASH_OPTIONS:
                        raise GraphOptionError('Invalid value to option %s' % option)
                    self.RRDGraphOptions[option_index + 1] = user_prefs[n+1]    # the next item in the RRDGraphOptions list
                                                    # (previously saved as pv) is replaced by the next item
                                                    # in the user_prefs list
                    #print "Replaced", option, "(", pv, ") with:", user_prefs[n+1]
                    skip_next = True    # This is set to true, so that in the next loop, option is not processed, since it has been processed
                                # in the current loop
            else:
                self.RRDGraphOptions.append(option)
                #print "Added", option
                
                # Try to get the next item of ``user_prefs``
                try:
                    nv = user_prefs[n+1]
                except IndexError:
                	# There is no next item
                    pass
                else:
                    if not nv.startswith('--') and nv[:3] not in self.NON_DASH_OPTIONS:
                        self.RRDGraphOptions.append(nv)
                        #print " with value", nv
                        skip_next = True

    def set_legend_column_titles_injection_point(self, reset=False):
        if reset:
            self.Legend_Column_Titles_Injection_Point = None
        elif self.Legend_Column_Titles_Injection_Point is not None:
            self.Legend_Column_Titles_Injection_Point = len(self.RRDGraphOptions) - 1

    def draw_graph(self, path, start='-1h', end='now'):
        """
        saves the graph at 'path'
        """
        # Merge time frame options
        self.merge_options( [ '--start', start ] )
        self.merge_options( [ '--end', end ] )
        #print repr(self.RRDGraphOptions)
        # Save the graph
        rrdtool.graph(path, *self.RRDGraphOptions)

    def get_options(self, start, end):
        """
        The same as the draw_graph method, but does not accept a path.
        It accepts starts and end times (formats acceptable by rrdtool)
        and adds them to the graph options and then returns all the options
        as a list.

        This is mainly to be used by dynamic pages.
        """
        # Merge time frame options
        self.merge_options( [ '--start', str(start) ] )
        self.merge_options( [ '--end', str(end) ] )
        # Return rrdgraph options
        return self.RRDGraphOptions

    def add_legend_column_titles(self, column_list, max_len):
        # Print graph time range
        #self.extend( [
        #    'COMMENT:From %s - %s\l' % ( 'TODO', datetime.datetime.now().strftime("%Y/%m/%d %H\:%M\:%S")),
        #    ] )
        #
        dd = 11
        legend_columns = ['COMMENT:' + ' '*max_len + ' '*2]
        comments = {
            'Last'    : 'COMMENT:' + ' '*abs(dd - len('Last')) + 'Last',
            'Min'    : 'COMMENT:' + ' '*abs(dd - len('Minimum')) + 'Minimum',
            'Avg'    : 'COMMENT:' + ' '*abs(dd - len('Average')) + 'Average',
            'Max'    : 'COMMENT:' + ' '*abs(dd - len('Maximum')) + 'Maximum',
            '95th'    : 'COMMENT:' + ' '*abs(dd - len('95th pctl')) + '95th pctl',
            }
        for column in column_list:
            #print repr(comments[column])
            legend_columns.append( comments[column] )
        # Add new line character to the last field
        legend_columns[-1] = legend_columns[-1] + '\l'
        #print legend_columns
        self.extend( legend_columns )
        self.HasLegendColumns = True

    def add_legend(self, variable, column_list):

        c2v2g = {
            'Last'    : [
                'VDEF:%slast=%s,LAST' % (variable, variable),
                'GPRINT:%slast:%s' % (variable, self.LegendFormat)
                ],
            'Min'    : [
                'VDEF:%smin=%s,MINIMUM' % (variable, variable),
                'GPRINT:%smin:%s' % (variable, self.LegendFormat)
                ],
            'Avg'    : [
                'VDEF:%savg=%s,AVERAGE' % (variable, variable),
                'GPRINT:%savg:%s' % (variable, self.LegendFormat)
                ],
            'Max'    : [
                'VDEF:%smax=%s,MAXIMUM' % (variable, variable),
                'GPRINT:%smax:%s' % (variable, self.LegendFormat),
                ],
            '95th'    : [
                'VDEF:%spct=%s,95,PERCENT' % (variable, variable),
                'GPRINT:%spct:%s\l' % (variable, self.LegendFormat)
                ]
            }
        for column in column_list:
            column_data = c2v2g[column]
            self.extend(column_data)

