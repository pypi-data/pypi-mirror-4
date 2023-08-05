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

from django.conf.urls.defaults import *


urlpatterns = patterns('sysscope.views',
    url(r'^$', 'start_view', name='start'),
    url(r'^(?P<section>[\-_\w]+)/(?P<start>[\-\w]+)/(?P<timeframe>[\w]+)/$', 'section_view', name='section'),
    url(r'^(?P<section>[\-_\w]+)/(?P<graph>[\-_\w]+)/$', 'graph_archive_view', name='graph_archive'),
    url(r'^images/(?P<section>[\-_\w]+)/(?P<graph>[\-_\w]+)/(?P<start>[\-\w]+)/(?P<timeframe>[\w]+)/graph.png$', 'graph_image_view', name='graph_image'),

)

