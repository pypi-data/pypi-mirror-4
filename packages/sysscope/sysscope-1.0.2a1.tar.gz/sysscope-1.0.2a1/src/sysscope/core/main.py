# -*- coding: utf-8 -*-
#
#  This file is part of sysscope.
#
#  sysscope - a graphing solution that facilitates the visual representation
#             of RRDtool's Round Robin Databases (RRD).
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

import os
import shutil
import datetime
import time

import config

def Main(SINGLE_SECTION):

	CONFIG_PATH = ''
	for loc in config.POSSIBLE_CONFIG_LOCATIONS:
		if os.path.exists(loc):
			CONFIG_PATH = loc

	TIME_FRAMES_ORDERED = ['h', 'd', 'w', 'm', 'y']
	TIME_FRAME_POOL = {
		'h' : ('-%s' % (60*60),		'Hour', '%s - Hourly Report'),
		'd' : ('-%s' % (60*60*24),	'Day', '%s - Daily Report'),
		'w' : ('-%s' % (60*60*24*7),	'Week', '%s - Weekly Report'),
		'm' : ('-%s' % (60*60*24*30),	'Month', '%s - Monthly Report'),
		'y' : ('-%s' % (60*60*24*365),	'Year', '%s - Yearly Report'),
		}

	CFG = config.ConfigFileParser(CONFIG_PATH)
	CFG.parse()

	#DATA_DIR = '/var/lib/sysscope/stats/'
	#DATA_DIR = 'outdir/'
	DATA_DIR = CFG.global_options['OutputDir']

	#shutil.rmtree(DATA_DIR, ignore_errors=True)

	if not os.path.exists(DATA_DIR):
		os.mkdir(DATA_DIR)
	if not os.path.exists(os.path.join(DATA_DIR, 'images')):
		os.mkdir(os.path.join(DATA_DIR, 'images'))

	for time_frame in TIME_FRAME_POOL.keys():
		# Create all section urls
		URLs = []
		for n, section in enumerate(CFG.sections_ordered):
			URLs.append( '<li><a href="section_%d_%s.html">%s</a></li>' % (n, time_frame, section.name ) )

		# create graphs and HTML files
		for n, section in enumerate(CFG.sections_ordered):

			if SINGLE_SECTION and section.name != SINGLE_SECTION:
				continue

			Graph_HTML = []
			for q, graph in enumerate(CFG.graphs[section.name]):
				path = os.path.join(DATA_DIR, 'images', 'graph_%d_%d_%s.png' % (n, q, time_frame))
				t_start = TIME_FRAME_POOL[time_frame][0]
				t_end = 'now'
				graph.draw_graph(path, t_start, t_end)
				Graph_HTML.append( '<div id="graph"><img src="%s" /></div>' % os.path.join('images', 'graph_%d_%d_%s.png' % (n, q, time_frame)) )

			time_current = time.time()
			start = int(time_current) - abs(int(TIME_FRAME_POOL[time_frame][0]))
			end = time_current
			path = os.path.join(DATA_DIR, 'section_%d_%s.html' % (n, time_frame))
			f = open(path, 'w')
			f.write(HTML % {
				'sections'	: ' '.join(URLs),
				'timeframes': get_time_frame_selector_options(TIME_FRAMES_ORDERED, TIME_FRAME_POOL, n, time_frame),	# n is Section ID,  time_frame  is the current time frame
				'graphs'	: '\n'.join(Graph_HTML),
				'section'	: n,
				'title'		: TIME_FRAME_POOL[time_frame][2] % section.name,
				'start'		: datetime.datetime.fromtimestamp(start).strftime('%a, %b %d %Y %H:%M:%S'),
				'end'		: datetime.datetime.fromtimestamp(end).strftime('%a, %b %d %Y %H:%M:%S'),
				})
			f.close()

def get_time_frame_selector_options(TIME_FRAMES_ORDERED, TIME_FRAME_POOL, section_id, cur_time_frame):
	options = []
	for frame in TIME_FRAMES_ORDERED:

		if frame == cur_time_frame:
			option = """<option value='section_%s_%s.html' selected> %s </option>""" % (section_id, frame, TIME_FRAME_POOL[frame][1])
		else:
			option = """<option value='section_%s_%s.html'> %s </option>""" % (section_id, frame, TIME_FRAME_POOL[frame][1])
		options.append(option)
		# Adds the following options:   	<option value='section_%(section)s_d.html'> Day </option>
	return '\n'.join(options)



