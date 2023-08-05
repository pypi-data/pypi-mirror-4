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

import sys
import os

from sysscope.core.commons import canonical_name
from sysscope.core import graphbase
from sysscope.core.syntax import Syntax, DEFAULT_LEGEND_COLUMNS
from sysscope.core.exceptions import sysscopeError


class ConfigSyntaxError(sysscopeError):
	def __init__(self, line_no, error_message):
		self.line_no = line_no
		self.value = error_message
	def __str__(self):
		return 'Syntax error in line %d. %s' % (self.line_no, self.value)

class ConfigFileError(sysscopeError):
	pass


class Section:
	def __init__(self, name):
		self.name = name
		self.canonical_name = canonical_name(name)
	def __str__(self):
		return self.name


POSSIBLE_CONFIG_LOCATIONS = [
	'/usr/local/etc/sysscope.conf',
	'/etc/sysscope.conf',
	'etc/sysscope.conf'
	]

	
def get_configuration(global_only):
	"""Helper function to get the configuration.
	
	Returns a sysscope.config.ConfigFileParser object
	"""
	CONFIG_PATH = ''
	for loc in POSSIBLE_CONFIG_LOCATIONS:
		if os.path.exists(loc):
			CONFIG_PATH = loc
	CFG = ConfigFileParser(CONFIG_PATH)
	CFG.parse(global_only=global_only)
	return CFG


class ConfigFileParser:

	COMMENT_CHAR = '#'

	def __init__(self, path):

		# Configuration file path
		if not path:
			raise ConfigFileError('Configuration file not found')
		self.path = path

		# How the configuration file is parsed:
		#
		# Each line is read from the config file and is put to the
		# 'ConfigLineStack' stack. The lines are put in raw mode into
		# the stack, meaning that no processing occurs during this
		# operation, apart from striping the line and not including
		# comments or empty lines.
		#
		# A function should pop() the configuration lines from the stack
		# in order to be processed.
		#
		# This method is required in case the config file is divided
		# into several smaller config files, which are imported into
		# the main config file with the 'Include' directive.
		self.ConfigLineStack = []

		# Holds the global options, eg logfile, output dir etc
		# Format: {
		#	'option1' : value,
		#	}
		self.global_options = {}

		# Holds the tree of sections and graphs
		# Format: {
		#	'section1' : [graph1, graph2, ...],
		#	'section2' : [graph4],
		#	}
		# Types:
		#   section : str
		#   graph : graphbase.Graph instance
		#
		self.graphs = {}

		# Holds the user-defined templates
		# Format: {
		#	'template1' : ['--opt1', 'opt1_value', '--opt2', --opt3', 'opt3_value', ...],
		#	}
		self.templates = {}

		# This is set to the name of the first template that is read from the config.
		# This is by convention considered the default template.
		self.default_template = None

		# Holds Section instances in the order sections are read from the config file.
		self.sections_ordered = []

		# 'reading_graph_options' signals the gathering of all the
		# next directives, until a '</Graph>' tag is met. These
		# directives are added to the following list as directive objects.
		self.graph_directives = []	# Should be reset after graph directives have been processed

		# Every time the parser enters a configuration block, it needs
		# to store some information that is relative to the current
		# configuration block or its parent blocks. This information is
		# stored into the following variables.
		self.current_section = ''	# Should be reset at </Section>
		self.current_section_rrdbase = ''	# Should be reset at </Section>
		self.current_template = ''	# Should be reset at </Template>
		self.current_graph = None	# Should be reset after graph directives have been processed

		# Switches
		# These boolean variables show what the parser is doin, eg
		# reading the template block.

		# 'processing_template' becomes True whenever directives within
		# a <Template..>...</Template> block are processed.
		self.processing_template = False	# Should be reset at </Template>

		# 'reading_graph_options' becomes True whenever a 'Graph' tag is met.
		self.reading_graph_options = False	# Should be reset at </Graph>

		# Read main config file
		self.read_config_file(path)


	def read_config_file(self, path):
		f = open(path)
		conflines = []
		for line in f:
			line = line.strip()
			# Empty lines and comments are excluded:
			if line and not line.startswith(self.COMMENT_CHAR):
				conflines.append(line)
		f.close()
		self.ConfigLineStack.extend( reversed(conflines) )


	def parse(self, global_only=False):
		"""Parses the config file.

		if 'global_only' is True, then only the directives in the GLOBAL
		namespace are parsed. Nothing else.
		"""

		# Counter that is used for line numbering.
		no = 0

		# Master syntax class
		# the parse_line() method returns an object of type 'tag' or 'directive'
		ConfSyntax = Syntax()

		# Iterate over the stack items.
		while self.ConfigLineStack:

			# retrieve one configuration line from the stack
			line = self.ConfigLineStack.pop()

			# Increment counter by one
			#
			# Special Note:
			# The lines inside a <Graph ..>...</Graph> block are first saved in the
			# 'self.graph_directives' list along with each line number (phase A)
			# and then they are processed (phase B).
			# In phase B (graph-directive processing mode) the counter should not be increased.
			if self.graph_directives and not self.reading_graph_options:
				pass
			else:
				no += 1

			# Get entity
			obj = ConfSyntax.parse_line(no, line)

			# Check for GLOBAL ONLY PARSING
			# If global_only parsing has been requested and the read
			# object is a tag or it is an 'Include' directive,
			# do nothing.
			if global_only:
				if obj.type == 'tag':
					continue
				elif obj.name == 'Include':
					continue

			# Include directive
			# This directive imports an additional configuration file into self.ConfigLineStack
			if obj.name == 'Include':

				path = obj.value
				self.read_config_file(path)
				continue

			if obj.type == 'tag':

				if obj.is_closing_tag:	# The line contains a CLOSING TAG

					# Reset the following variables
					if obj.name == 'Section':
						self.current_section = ''
						self.current_section_rrdbase = ''
					elif obj.name == 'Template':
						self.current_template = ''
						self.processing_template = False
					elif obj.name == 'Graph':
						self.reading_graph_options = False

				else:			# The line contains an OPENING TAG

					# Process Tags

					if obj.name == 'Section':
						section_name = obj.value

						# Set the section that is being processed
						self.current_section = section_name
						# Add the section to the list, which contains the order of the sections
						self.sections_ordered.append( Section(section_name) )
						# Add the new section in the graphs dictionary
						self.graphs[section_name] = []

					elif obj.name == 'Template':
						template_name = obj.value

						# Set the current_template
						self.current_template = template_name
						# Add the template to self.templates
						self.templates[template_name] = []
						# Set the default template if it hasn't been set.
						# This way the default template is always the first one that is read from the config
						if not self.default_template:
							self.default_template = template_name
						# Set template-processing mode
						self.processing_template = True

					elif obj.name == 'Graph':
						graph_name = obj.value

						# Create instance of graph...
						GraphRRD = graphbase.Graph(graph_name)
						# ... add it to the current section's list graphs
						self.graphs[self.current_section].append( GraphRRD )
						# ... set the currently processed graph to 'GraphRRD'
						self.current_graph = GraphRRD
						# ... set graph-directive-gathering mode
						self.reading_graph_options = True

			elif self.processing_template:	# Template block processing mode

				# Process directives within the <Template ...> ... </Template> block.
				directive, directive_data = obj.name, obj.value

				if directive in ('Option', 'RawOption'):

					parts = directive_data.split(' ', 1)
					# Add the option
					if directive == 'Option':
						option = '--%s' % parts[0]
					else:
						option = parts[0]
					self.templates[self.current_template].append(option)
					# Add the value, if applicable
					if len(parts) > 1:
						option_value = parts[1]
						self.templates[self.current_template].append(option_value)

			elif self.reading_graph_options:	# Graph-directive gathering mode

				# This should *READ* lines that are within the <Graph ...> ... </Graph> block.
				# The directive object is added to the 'self.graph_directives' list
				self.graph_directives.append( obj )

			elif obj.type == 'directive':	# If it is any other directive __outside__ <Graph>...</Graph> or <Template>...</Template>

				directive, directive_data = obj.name, obj.value
				#print 'Processing', directive, directive_data
				self.global_options[directive] = directive_data
				if directive == 'RRDBase':
					self.current_section_rrdbase = directive_data

			if self.graph_directives and not self.reading_graph_options:		# Graph-directive processing mode

				# This should *PROCESS* self.current_graph's SAVED directives
				# (lines that have been read from a <Graph ...> ... </Graph> block)

				# Default template
				# As default template is considered the the first <Template..>...</Template> block
				# If a template is not defined for a graph using the 'TemplateName' directive, then
				# the default template is used.
				if not sum(1 for dctv in self.graph_directives if dctv.name == 'TemplateName'):
					# If TemplateName is not used in the current graph, use the default template
					#print "Using DEFAULT Template %s" % self.default_template
					self.current_graph.merge_options( self.templates[self.default_template] )

				# Process Legend-related directives.

				# DoLegend
				# By default, each 'DrawGraph' variable is added to the legend
				# and 'Last','Min','Avg','Max','95th' items are displayed.
				# The following gets False when a 'Legend off' directive is met.
				DoLegend = True
				for dctv in self.graph_directives:
					if dctv.name == 'Legend' and dctv.value == 'Off':
						DoLegend = False

				# legend_columns
				# Determine legend columns
				if DoLegend:
					legend_columns = DEFAULT_LEGEND_COLUMNS
					for dctv in self.graph_directives:
						if dctv.name == 'LegendColumns':
							# Get a list of legend columns, eg ['Last', 'Min', 'Avg', 'Max']
							legend_columns = [col.strip() for col in dctv.value.split(',') if col.strip()]

				# longest_legend_label_len
				# Determine the length of the longest legend label.
				if DoLegend:
					longest_legend_label_len = 0
					for dctv in self.graph_directives:
						if dctv.name == 'DrawGraph':
							legend_label = dctv.value[-1]
							if len(legend_label) > longest_legend_label_len:
								longest_legend_label_len = len(legend_label)

				# Process other directives
				for graph_directive in self.graph_directives:

					# Store the saved line number and the saved directive value in new variables.
					# 'saved_no' should be used in error messages in this mode. This represents
					# the actual config line number. 'no' remains unchanged in this mode.
					directive = graph_directive.name
					directive_data = graph_directive.value
					saved_no = graph_directive.line

					if directive == 'TemplateName':
						#print repr(self.templates[directive_data])
						# If the default template has been used, it is impossible to enter in here.
						self.current_graph.merge_options( self.templates[directive_data] )

					elif directive == 'Legend':
						if directive_data == 'Off':
							self.current_graph.append('--no-legend')
							# DoLegend has already been set to False

					elif directive == 'LegendColumns':
						# Already processed
						pass

					elif directive == 'LegendFormat':
						self.current_graph.LegendFormat = directive_data

					elif directive == 'VerticalLabel':
						self.current_graph.extend( ['--vertical-label', directive_data] )

					elif directive == 'Option':
						rrdgraph_option = '--%s' % directive_data
						self.current_graph.merge_options(rrdgraph_option.split(' ', 1))

					elif directive == 'RawOption':
						rrdgraph_option = directive_data
						self.current_graph.merge_options(rrdgraph_option.split(' ', 1))

					elif directive == 'DataSource':
						# Syntax:
						#   DataSource <variable_name> </path/to/file.rrd>::<DS>::<RRA>

						# Set new variables for the  contents of the directive
						variable = graph_directive.var
						rrd_path, ds, rra = directive_data

						# Translate RRDBase, if it exists in the rrd path
						rrd_path = rrd_path.replace('@RRDBase@', self.current_section_rrdbase)

						# Construct rrdtool DEF statement and add it to the current graph
						RRD_DEF = 'DEF:%s=%s:%s:%s' % (variable, rrd_path, ds, rra)
						self.current_graph.append(RRD_DEF)

					elif directive == 'Consolidate':
						# Syntax:
						#   Consolidate <variable_name> <RPN_expression>

						# Set new variables for the  contents of the directive
						variable = graph_directive.var
						variable_data = directive_data

						# Construct rrdtool CDEF statement and add it to the current graph
						RRD_CDEF = 'CDEF:%s=%s' % (variable, variable_data)
						self.current_graph.append(RRD_CDEF)

					elif directive == 'DrawGraph':
						# Syntax:
						#   DrawGraph <variable_name> <type>::<color>::<legend_label>

						# Add legend column titles.
						if DoLegend and not self.current_graph.HasLegendColumns:
							self.current_graph.add_legend_column_titles(legend_columns, longest_legend_label_len)

						# Set new variables for the  contents of the directive
						variable = graph_directive.var
						graph_type, graph_color, var_label = directive_data

						# Hidden feature:
						# If the graph is a line (LINE{1,2,3}), but the word AREA has
						# concatenated, eg LINE1AREA, then an area of the same color but with
						# an alpha of '33' is added. this produces a sexier graph.
						is_sexy = False	# get True if eg LINE1AREA has been requested.
						if graph_type.startswith('LINE') and graph_type.endswith('AREA'):
							graph_type = graph_type[:-4]	# Keep the proper line type
							is_sexy = True

						# Color can be empty in order to prevent the graph item from being drawn.
						# This is needed because if the user does not want to enter a color,
						# he MUST leave an empty space between the '::' separators.
						graph_color = graph_color.strip()

						if DoLegend:
							var_label = var_label + ' '*(longest_legend_label_len-len(var_label))
						RRD_GRAPH = '%s:%s%sFF:%s' % (graph_type, variable, graph_color, var_label)
						self.current_graph.append(RRD_GRAPH)

						# Also add the extra AREA if 'LINEXAREA' had been requested
						if is_sexy:
							RRD_GRAPH = '%s:%s%s33:%s' % ('AREA', variable, graph_color, '')
							self.current_graph.append(RRD_GRAPH)
						# Also, add the legend.
						if DoLegend:
							self.current_graph.add_legend(variable, legend_columns)

					elif directive == 'VDataSource':
						# Syntax:
						#   VDataSource <variable_name> <RPN_expression>

						# Set new variables for the  contents of the directive
						variable = graph_directive.var
						variable_data = directive_data

						# Construct rrdtool CDEF statement and add it to the current graph
						RRD_CDEF = 'VDEF:%s=%s' % (variable, variable_data)
						self.current_graph.append(RRD_CDEF)

					elif directive == 'Gprint':
						# Syntax:
						#   Gprint <variable>::<format>

						RRD_GRAPH = 'GPRINT:' + ':'.join(directive_data)	# directive_data is a list
						self.current_graph.append(RRD_GRAPH)

					elif directive == 'Comment':
						# Syntax:
						#   Comment <data>

						RRD_GRAPH = 'COMMENT:' + directive_data	# directive_data is a string for this directive
						self.current_graph.append(RRD_GRAPH)

					elif directive == 'Hrule':
						# Syntax:
						#   Hrule <data>

						RRD_GRAPH = 'HRULE:' + directive_data	# directive_data is a string for this directive
						self.current_graph.append(RRD_GRAPH)

					elif directive == 'Vrule':
						# Syntax:
						#   Vrule <data>

						RRD_GRAPH = 'VRULE:' + directive_data	# directive_data is a string for this directive
						self.current_graph.append(RRD_GRAPH)

				# All graph directives in 'self.graph_directives' have been processed.

				# 'self.current_graph' & 'self.graph_directives' are reset here
				self.current_graph = None
				self.graph_directives = []


