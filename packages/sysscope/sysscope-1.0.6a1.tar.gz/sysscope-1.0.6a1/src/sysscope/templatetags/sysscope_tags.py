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

"""
In order to use these template tags you need to use the following in your templates

{% load sysscope_tags %}

"""

from django import template

from sysscope.utils import TIME_FRAME_POOL
from sysscope.utils import TIME_FRAMES_ORDERED
from sysscope.utils import get_section_report_title



register = template.Library()



@register.inclusion_tag('sysscope/section_links.html')
def graph_section_links(CFG, start, timeframe):
    return {
        'CFG': CFG,
        'start': start,
        'timeframe': timeframe,
        }


@register.inclusion_tag('sysscope/archive_links.html')
def graph_archive_links(CFG, section_obj, graph_obj, graph_list, start, timeframe):
    return {
        'CFG': CFG,
        'section_obj': section_obj,
        'graph_obj': graph_obj,
        'graph_list': graph_list,
        'start': start,
        'timeframe': timeframe,
        }


@register.inclusion_tag('sysscope/nav_timeframe_selector.html')
def nav_timeframe_selector(section_obj, current_timeframe):
    return {
        'section_obj': section_obj,
        'current_timeframe': current_timeframe,
        'timeframe_list': TIME_FRAMES_ORDERED,
        }


@register.inclusion_tag('sysscope/nav_timeframe_browser.html')
def nav_timeframe_browser(section_obj, current_start, current_timeframe):
    return {
        'section_obj': section_obj,
        'current_start': current_start,
        'current_timeframe': current_timeframe,
        'timeframe_list': TIME_FRAMES_ORDERED,
        }


@register.simple_tag
def section_report_title(section_obj, start, timeframe):
    return get_section_report_title(section_obj, start, timeframe)


@register.filter
def negative(value):
    return '-%s' % value


@register.filter
def timelyadverb(value):
    try:
        return TIME_FRAME_POOL[value][2]
    except KeyError:
        try:
            int(value)
        except ValueError:
            raise Exception('Invalid timeframe: %s' % repr(timeframe))
        else:
            return value


@register.filter
def friendlytime(value):
    try:
        return TIME_FRAME_POOL[value][1]
    except KeyError:
        try:
            int(value)
        except ValueError:
            raise Exception('Invalid timeframe: %s' % repr(timeframe))
        else:
            return value

