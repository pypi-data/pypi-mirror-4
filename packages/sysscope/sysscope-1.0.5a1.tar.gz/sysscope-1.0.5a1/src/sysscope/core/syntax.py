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

import re

from sysscope.core.exceptions import sysscopeError

#
# Constants
#

# Legend Columns
VALID_LEGEND_COLUMNS = ['Last', 'Min', 'Avg', 'Max', '95th']
DEFAULT_LEGEND_COLUMNS = VALID_LEGEND_COLUMNS

# Log Levels
VALID_LOG_LEVELS = ['debug', 'info', 'warning', 'error', 'critical']

#
# Custom Exceptions
#

class BaseSyntaxError(sysscopeError):
	def __init__(self, line_no, error_message):
		self.line_no = line_no
		self.value = error_message
		self.msg = 'syntax error in line %d. %s' % (self.line_no, self.value)
	def __str__(self):
		return self.msg

class GeneralSyntaxError(BaseSyntaxError):
	def __str__(self):
		return 'General Error: "%s"' % self.msg

class TagSyntaxError(BaseSyntaxError):
	def __str__(self):
		return 'Tag Error: "%s"' % self.msg

class DirectiveSyntaxError(BaseSyntaxError):
	def __str__(self):
		return 'Directive Error: "%s"' % self.msg

#
# Tag classes
#

class BaseTag:
	"""The base of Tag classes.

	Each tag has the following attributes:

	line		: the line number at which the directive exists in the config
	type		: 'tag'
	name		: the name of the tag
	value		: the data
	is_closing_tag	: boolean
	"""
	def __init__(self, name, data, is_closing_tag):
		self.line = 0
		self.type = 'tag'
		self.name = name
		self.value = None
		self.is_closing_tag = is_closing_tag
	def get_value(self, data):
		return data

class TagSimple(BaseTag):
	"""
	Syntax:
		<Tag>
	"""
	pass

class TagSpecial(BaseTag):
	"""
	Syntax:
		<Tag This is the data>
	"""
	def __init__(self, name, data, is_closing_tag):
		BaseTag.__init__(self, name, data, is_closing_tag)
		self.value = self.get_value(data)
	def get_value(self, data):
		if not self.is_closing_tag and not data.strip():
			raise TagSyntaxError('Invalid tag syntax')
		return data

#
# Directive
#

class BaseDirective:
	def __init__(self, name, data, syntax):
		"""
		self.data is set by derived classes by using the get_value() method.
		"""
		self.line = 0
		self.type = 'directive'
		self.name = name
		self.data = data
		self.var = self.get_var()
		self.value = self.get_value(syntax)	# --> CAN BE A STRING OR A LIST ACCORDING TO THE SYNTAX OF THE DIRECTIVE
	def get_var(self):
		"""Override"""
		pass
	def get_value(self, syntax):
		"""May be overridden"""
		if not syntax:
			return self.data	# Returns STRING
		m = re.match(syntax, self.data)
		if m:
			return list(m.groups())	# Returns LIST
		else:
			raise DirectiveSyntaxError('Invalid directive syntax')

class DirectiveSimple(BaseDirective):
	"""
	Syntax:
		Directive data
	"""
	pass

class DirectiveSpecial(BaseDirective):
	"""
	Syntax:
		Directive variable_name data
	"""
	def get_var(self):
		"""Sets the variable_name"""
		directive_data = self.data.split(' ', 1)
		if len(directive_data) >= 2:
			self.data = directive_data[1]
			return directive_data[0]
		else:
			raise DirectiveSyntaxError('Invalid directive syntax')

#
# Value validator Classes
#

class ValueValidatorBase:
	def __init__(self, valid_values):
		"""
		valid_values : list
		"""
		self.valid_values = valid_values
	def verify(self):
		"""override"""
		pass

class ValueValidatorSingle(ValueValidatorBase):
	def verify(self, value):
		"""
		value : string
		"""
		if value not in self.valid_values:
			return False
		return True

class ValueValidatorList(ValueValidatorBase):
	def verify(self, values):
		"""
		values : string (contains the comma separated list
		"""
		values_list = [val.strip() for val in values.split(',') if val.strip()]
		for value in values_list:
			if value not in self.valid_values:
				return False
		return True

#
# Main Syntax Classes
#

class Syntax(dict):
	"""Master Syntax Class.

	Basic Syntax
	------------
	The syntax of the sysscope configuration file is an Apache-style
	syntax. It consists of statements:

		Directive data

	or

		<Tag blah blah>
		...
		</Tag>


	Modular Configuration File
	--------------------------
	The configuration file may contain the directive 'Include'. This
	directive is not part of the actual sysscope configuration file syntax.
	Its syntax is:

		Include /path/to/file.conf

	Whenever it is met, it causes the config parser to include
	/path/to/file.conf

	It may be placed anywhere within the configuration file.


	Directive Placement
	-------------------
	Directives may be placed within a block defined by an opening tag (eg.
	<Tag blah>) and a closing tag (eg. </Tag>) and have an effect within the
	specific configuration block.
	Directives may also be placed outside <Tag>...</Tag> blocks. In such a
	case the directives belongs to the 'GLOBAL' scope and have effect
	throughout the configuration file.


	Tag Types
	---------
	Thre are two types of tags:

	1. Simple Tags: <Tag>...</Tag>
	2. Special Tags: <Tag blah blah>...</Tag>


	Directive Types
	---------------
	There two types of directives:

	1. Simple directives: consist of two parts:
		a) the directive name
		b) the data:
	   Example:
	   	Directive data

	2. Special directives: consist of three parts:
		a) the directive name
		b) a variable name, to which the data is assigned. The variable
		   can then be used by subsequent directives.
		c) the data
	   Example:
	   	Directive variable_name data


	Miscellaneous Info
	------------------
	Lines beginning with the '#' character (without quotes) are considered
	as comments.

	Empty lines mean nothing.

	Leading spaces mean nothing.


	Class Structure
	---------------
	This class is a dictionary (dictA) containing all the syntax details.

	The 'keys' of the dictionary should be the names of all the valid
	tag names without any of the characters <,>,/. A special tag name
	is 'GLOBAL' which represents the 'root namespace' of the configuration
	file. For example:

		self['GLOBAL'] = {...}
		self['Tag1'] = {...}
		...
		self['TagN'] = {...}

	Each key's value is another dictionary (dictB) containing those tag and
	directive names that are valid within the key's namescpace.
	dictB's syntax is:

		{
		'tag1'		: ...,
		'directive1'	: ...,
		'directive2'	: ...,
		}

	The value of each of the dictB keys varies according to the type (tag or
	directive) of the key.

	For tags, the value is just the relevant tag class name.

	For directives, the value is a tuple consisting of three items:

		( item1, item2, item3 )

		item1 : is the name of the relevant directive class.
		item2 : is a regular expression, which matches the format of the
		        directive's data
		item3 : is an *instance* of a validator class. The list of the
		        valid values for the directive is passed to the
		        constructor of the validator.

	The format of the dictionary is outlined below for tags (a) and
	directives (b).

	(a) 'Tag' : TagSpecial

	(b) 'Directive' : (
			directive_class,
			value_syntax_using_regex OR '' (if empty),
			ValidatorClass( [valid_value_1, valid_value_2, ...] ) OR None,
			)
	"""

	def __init__(self):
		"""Master Syntax Instance Constructor"""

		self['GLOBAL'] = {
			'Include'	: ( DirectiveSimple, '', None ),
			'OutputDir'	: ( DirectiveSimple, '', None ),
			'Logfile'	: ( DirectiveSimple, '', None ),
			'LogLevel'	: ( DirectiveSimple, '', ValueValidatorList(VALID_LOG_LEVELS) ),
			'OptionCacheDir': ( DirectiveSimple, '', None ),
			'Template'	: TagSpecial,
			'Section'	: TagSpecial,
			}

		self['Template'] = {
			'Include'	: ( DirectiveSimple, '', None ),
			'Option'	: ( DirectiveSimple, '', None ),
			'RawOption'	: ( DirectiveSimple, '', None ),
			}

		self['Section'] = {
			'Include'	: ( DirectiveSimple, '', None ),
			'RRDBase'	: ( DirectiveSimple, '', None ),
			'Graph'		: TagSpecial,
			}

		self['Graph'] = {
			'Include'	: ( DirectiveSimple, '', None ),
			'TemplateName'	: ( DirectiveSimple, '', None ),
			'Legend'	: ( DirectiveSimple, '', ValueValidatorSingle(['On', 'Off']) ),
			'LegendColumns'	: ( DirectiveSimple, '', ValueValidatorList(VALID_LEGEND_COLUMNS) ),
			'LegendFormat'	: ( DirectiveSimple, '', None ),
			'VerticalLabel'	: ( DirectiveSimple, '', None ),
			'Option'	: ( DirectiveSimple, '', None ),
			'RawOption'	: ( DirectiveSimple, '', None ),
			'DataSource'	: ( DirectiveSpecial, '(.*)::(.*)::(.*)', None ),
			'VDataSource'	: ( DirectiveSpecial, '', None ),
			'Consolidate'	: ( DirectiveSpecial, '', None ),
			'DrawGraph'	: ( DirectiveSpecial, '(.*)::(.*)::(.*)', None ),
			'Gprint'	: ( DirectiveSimple, '(.*)::(.*)', None ),
			'Comment'	: ( DirectiveSimple, '', None ),
			'Hrule'		: ( DirectiveSimple, '', None ),
			'Vrule'		: ( DirectiveSimple, '', None ),
			}

		# Open_Tags
		# When an opening tag is first met, it is added to this list.
		# When the last tag of the list is closed, then it is removed.
		# Initially the list contains the root tag 'GLOBAL'.
		self.Open_Tags = ['GLOBAL']

	def parse_line(self, line_no, line):
		"""Parses 'line' and returns an instance of the directive or tag.

		'line' should be already stripped.

		entity entity_data

		tag_name tag_data
		directive_name directive_data
		directive_name variable_name directive_data

		"""
		#print "-"*40
		#print "Processing:", line
		#print self.Open_Tags
		#print "-"*40
		# Preliminary check if line contains an opening/closing Tag
		is_tag = False
		is_tag_closing = False
		if line.startswith('<') and line.endswith('>'):
			is_tag = True
			line = line.strip('<>')
		if line.startswith('/'):
			is_tag_closing = True
			line = line.lstrip('/')

		# Split the line at the first empty space
		# This returns the entity (directive/tag) name and its associated data.
		# NOTE: data does not exist for all closing tags and for simple tags
		parts = line.split(' ', 1)
		if len(parts) == 1:
			entity, entity_data = parts[0], ''	# For 'simple tags' or 'closing tags' entity data is ''
		else:
			entity, entity_data = parts[0], parts[1]	# For 'special tags', 'simple directives', 'special directives'

		# Set the parent_tag
		# 'parent_tag' is the container for the currently processed directive or tag
		# Usually, the parent tag is the last item of the self.Open_Tags list,
		# except for the case where the line contains a closing tag.
		# In such a case, the last item of the self.Open_Tags list is deleted
		# before the parent_tag is set.
		if is_tag_closing:
			if self.Open_Tags[-1] == entity:
				del self.Open_Tags[-1]
			else:
				raise TagSyntaxError(line_no, 'Tag \'%s\' has not been previously opened' % entity)
		# Now, parent_tag is set
		parent_tag = self.Open_Tags[-1]

		# Error checking
		if not self.has_key(parent_tag) or not self[parent_tag].has_key(entity):
			error_msg = '\'%s\' not allowed in this context' % entity
			if is_tag:
				raise TagSyntaxError(line_no, error_msg)
			else:
				raise DirectiveSyntaxError(line_no, error_msg)

		# Open_Tags management
		if is_tag:
			if is_tag_closing:
				# The closing tag has already been removed from the list
				pass
			else:
				# Add the tag to the list of the currently opened tags
				self.Open_Tags.append(entity)

		#
		# Process the Tag or Directive data
		#

		# entity_data_syntax contains the syntax information, which is
		# a class name for tags or a tuple for directives
		entity_data_syntax = self[parent_tag][entity]

		# For directives, entity_data_syntax is a tuple containing syntax information
		if type(entity_data_syntax) is tuple:	# Is directive

			# if 'is_tag' *is* enabled then an error has occured
			if is_tag:
				raise TagSyntaxError(line_no, '\'%s\' is not a valid tag' % entity)

			directive_class, directive_value_syntax, value_validator = entity_data_syntax
			obj = directive_class(entity, entity_data, directive_value_syntax)
			if value_validator:
				if not value_validator.verify(obj.value):
					raise DirectiveSyntaxError(line_no, 'Invalid directive value')
			obj.line = line_no	# Set the line number in the directive obj
			return obj

		# For tags, entity_data_syntax is a class name
		else:	# Is a tag

			# if 'is_tag' *is*not* enabled then an error has occured
			if not is_tag:
				raise DirectiveSyntaxError(line_no, '\'%s\' is not a valid directive' % entity)

			tag_class = entity_data_syntax
			obj = tag_class(entity, entity_data, is_tag_closing)
			obj.line = line_no	# Set the line number in the tag obj
			return obj



