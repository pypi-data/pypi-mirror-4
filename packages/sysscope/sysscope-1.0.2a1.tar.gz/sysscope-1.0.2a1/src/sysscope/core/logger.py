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

import logging
from sysscope.core.exceptions import sysscopeError
from sysscope import get_version

DEFAULT_LEVELS = {
	"debug"		: logging.DEBUG,
	"info"		: logging.INFO,
	"warning"	: logging.WARNING,
	"error"		: logging.ERROR,
	"critical"	: logging.CRITICAL,
	}

class LoggerError(sysscopeError): pass

def get_sysscope_logger(settings):
	"""Creates and returns a logger object.
	
	This is where handlers are attached to the logger object.
	A Streamhandler is always attached, while a Filehandler is attached
	only if it has been enabled in the 'logging' settings.
	
	Returns the logger object.
	"""
	facilities = []	# holds strings specific to each enabled handler
	logger = logging.getLogger('sysscope')
	try:
		logger.setLevel(DEFAULT_LEVELS[settings["log_level"].lower()])
	except KeyError, err:
		raise LoggerError("Incorrect logging level '%s'" % err)
	else:
		#
		# Add stderr handler
		#
		stderr_handler = logging.StreamHandler()
		stderr_formatter = logging.Formatter("%(name)s:%(levelname)-8s %(message)s")
		stderr_handler.setFormatter(stderr_formatter)
		logger.addHandler(stderr_handler)
		facilities.append("stderr")
		#
		# Add file handler
		#
		if int(settings["enable_log_file"]):
			if settings["log_file_path"]:
				try:
					file_handler = logging.FileHandler(settings["log_file_path"], "a")
				except IOError, err:
					raise LoggerError("%s: '%s'" % (err[1], settings["log_file_path"]))
				else:
					file_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S')
					file_handler.setFormatter(file_formatter)
					logger.addHandler(file_handler)
					facilities.append("file")
			else:
				raise LoggerError("No logfile has been specified")
		logger.info("%s v%s starting up..." % ('sysscope', get_version()))
		logger.info("logger initialization complete.")
		logger.info("enabled logging facilities: %s" % ", ".join(facilities))
	return logger


