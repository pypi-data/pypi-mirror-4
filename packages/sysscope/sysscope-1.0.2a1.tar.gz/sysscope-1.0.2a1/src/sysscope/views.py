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
import datetime

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse

from sysscope import get_version
from sysscope.models import CFG
from sysscope.utils import get_graph_times
from sysscope.core.config import Section
from sysscope.core.commons import get_graph_image_data
from sysscope.utils import formatted_time
from sysscope.utils import resolve_time
from sysscope.utils import TIME_FRAMES_ORDERED


@login_required
def start_view(request):
    info_dict = {
        'CFG': CFG,
        'start' : '-d',
        'timeframe': 'd',
        'version'   : get_version(),
    }
    return render_to_response(
        'sysscope/start.html', info_dict, context_instance=RequestContext(request), mimetype='text/html')


@login_required
def section_view(request, section, start, timeframe):
    
    if request.method == 'POST':
        #raise Exception(repr(request.META))
        selected_timeframe = request.POST.get('selected_timeframe', None)
        backward = request.POST.get('backward', None)
        forward = request.POST.get('forward', None)
    
        if selected_timeframe:
            
            # Check value
            if selected_timeframe not in TIME_FRAMES_ORDERED:
                try:
                    int(selected_timeframe)
                except ValueError:
                    return HttpResponseBadRequest
            
            timestamp_current = resolve_time(start)
            timestamp_from_selection = resolve_time(selected_timeframe)
                
            if backward:
                start = '-%d' % (timestamp_current + timestamp_from_selection)
                timeframe = selected_timeframe
            
            elif forward:
                start = '-%d' % (timestamp_current - timestamp_from_selection)
                timeframe = selected_timeframe
                
            return HttpResponseRedirect(reverse('section', kwargs={
                'section': section,
                'start': start,
                'timeframe': timeframe,
                }))

    # Find section object by its canonical name
    for section_obj in CFG.sections_ordered:
        if section_obj.canonical_name == section:
            break
    
    # Get graph list and break
    graph_list = CFG.graphs.get(section_obj.name, None)
    
    if not graph_list:
        return HttpResponseNotFound
    
    # Get times
    t_start, t_end, t_frame = get_graph_times(start, timeframe)
    
    info_dict = {
        'CFG': CFG,
        'section_obj': section_obj,
        'start' : start,
        'timeframe': timeframe,
        'graph_list': graph_list,
        'version'   : get_version(),
        't_start': datetime.datetime.fromtimestamp(t_start),
        't_end': datetime.datetime.fromtimestamp(t_end),
    }
    return render_to_response(
        'sysscope/section.html', info_dict, context_instance=RequestContext(request), mimetype='text/html')


@login_required
def graph_archive_view(request, section, graph):
    
    # TODO: add method CFG.section_exists()
    # Find section object by its canonical name
    for section_obj in CFG.sections_ordered:
        if section_obj.canonical_name == section:
            break
    
    # Get graph list and break
    graph_list = CFG.graphs.get(section_obj.name, None)
    
    if not graph_list:
        return HttpResponseNotFound
    
    # TODO: add method CFG.graph_exists()
    graph_found = False
    for graph_obj in graph_list:
        if graph_obj.CanonicalName == graph:
            # Break! Graph found!
            graph_found = True
            break
    
    if not graph_found:
        return HttpResponseNotFound
    
    # Get times
    #time_current = time.time()
    #t_start, t_end, t_frame = get_graph_times(time_current, start, timeframe)
    
    info_dict = {
        'CFG': CFG,
        'section_obj': section_obj,
        'graph_obj': graph_obj,
        'graph_list': graph_list,
        'start' : '-d',
        'timeframe': 'd',
        'timeframe_list': ['H', 'd', 'w', 'm', 'y'],
        'version'   : get_version(),
    }
    return render_to_response(
        'sysscope/graph_archive.html', info_dict, context_instance=RequestContext(request), mimetype='text/html')


@login_required
def graph_image_view(request, section, graph, start, timeframe):
    # TODO: add method CFG.section_exists()
    # Find section object by its canonical name
    for section_obj in CFG.sections_ordered:
        if section_obj.canonical_name == section:
            break
    
    # Get graph list and break
    graph_list = CFG.graphs.get(section_obj.name, None)
    
    if not graph_list:
        return HttpResponseNotFound
    
    # TODO: add method CFG.graph_exists()
    graph_found = False
    for graph_obj in graph_list:
        if graph_obj.CanonicalName == graph:
            # Break! Graph found!
            graph_found = True
            break
    
    if not graph_found:
        return HttpResponseNotFound
    
    t_start, t_end, t_frame = get_graph_times(start, timeframe)
    
    # rrdgraph options
    rrd_options = graph_obj.get_options(start=t_start, end=t_end)
    image_data = get_graph_image_data(rrd_options)
    
    response = HttpResponse(image_data, content_type='image/png')
    response['Cache-Control'] = 'max-age=0, no-store, no-cache, must-revalidate'
    return response


    

    