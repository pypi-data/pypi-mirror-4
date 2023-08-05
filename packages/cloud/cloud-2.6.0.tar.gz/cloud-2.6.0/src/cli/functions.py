"""
Functions wrap PiCloud calls

"""
"""
Copyright (c) 2012 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

email: contact@picloud.com

The cloud package is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this package; if not, see 
http://www.gnu.org/licenses/lgpl-2.1.html    
"""

"""TODO:
Add rest publishing..
result (to get things from rest)
"""

import os
import random
import sys
import getpass

try:
    import json
except:
    # Python 2.5 compatibility
    import simplejson as json

from itertools import izip
from subprocess import Popen, PIPE

# TODO: Must move this out of CLI into shell-exec.....
from .. import shell
from .. import _getcloud
from ..cloud import CloudException
from ..util import template, OrderedDict
from ..util.xrange_helper import PiecewiseXrange, maybe_xrange_iter
from ..rest import _invoke

def _gen_shell_kwargs(extra_args):
    kwargs = {}
    for arg, val in extra_args.items():
        if val == None: #default/not present
            continue        
        if arg == 'depends_on':
            arg = parse_jids(arg)
        kwargs['_' + arg] = val
    return kwargs
        

def execute(command, args, return_file, ignore_exit_status, cwd=None, **kwargs):
    command = ' '.join(command)
    
    #return cloud.call(execute_program, command)
    arg_dct = template.extract_args(args, allow_map = False)
    kwargs = _gen_shell_kwargs(kwargs)
    
    jid = shell.execute(command, arg_dct, return_file, ignore_exit_status, cwd, **kwargs)
    
    cloud = _getcloud()
    if cloud.adapter.connection.is_simulated(): # on simulation wait for job to complete
        return result(str(jid))
    else:  # only return jid when not simulating
        return jid
    
def execute_map(command, args, mapargs, return_file, ignore_exit_status, cwd=None, **kwargs):
    command = ' '.join(command)
    arg_dct = template.extract_args(args, allow_map = False)
    if not mapargs:
        raise ValueError('At least one -n (--map-data) parameter must be provided')
    
    maparg_dct = template.extract_args(mapargs, allow_map = True)
    kwargs = _gen_shell_kwargs(kwargs)
    
    jids = shell.execute_map(command, arg_dct, maparg_dct, return_file, 
                             ignore_exit_status, cwd, **kwargs)
    cloud = _getcloud()
    if cloud.adapter.connection.is_simulated(): # on simulation wait for job to complete
        return result('%s-%s' % (jids[0], jids[-1]))
    else:  # only return jid when not simulating
        if isinstance(jids, xrange):
            return '%s-%s' % (jids[0], jids[-1])
        else:
            return jids
        
def rest_publish(command, label, return_file, ignore_exit_status, **kwargs):
    command = ' '.join(command)

    kwargs = _gen_shell_kwargs(kwargs)
    
    return shell.rest_publish(command, label, return_file, ignore_exit_status, **kwargs)

def cron_register(command, label, schedule, return_file, ignore_exit_status, **kwargs):
    command = ' '.join(command)

    kwargs = _gen_shell_kwargs(kwargs)
    
    return shell.cron_register(command, label, schedule, return_file, ignore_exit_status, **kwargs)


"""other rest"""
def _handle_file_upload(arg):
    if arg.startswith('@'):
        filename = arg[1:]
        return open(filename)
    else:
        return arg
    

def rest_invoke(label, args):
    arg_dct = template.extract_args(args, allow_map = False)
    listified_args = dict((name, [_handle_file_upload(val)]) for name, val in arg_dct.items())
    return _invoke(label, listified_args, is_map = False)

def rest_invoke_map(label, args, mapargs):
    if not mapargs:
        raise ValueError('At least one -n (--map-data) parameter must be provided')
    
    single_arg_dct = template.extract_args(args, allow_map = False)
    map_arg_dct = template.extract_args(mapargs, allow_map = True)
    
    for kwd, arg in single_arg_dct.items():
        map_arg_dct[kwd] = [arg]
        
    for kwd, arglist in map_arg_dct.items():
        map_arg_dct[kwd] = [_handle_file_upload(arg) for arg in arglist]
    
    jids = _invoke(label, map_arg_dct, is_map = True)
    if isinstance(jids, xrange):
        return '%s-%s' % (jids[0], jids[-1])
    else:
        return jids

    
""" todo: kill, status, etc. on formatted jids"""
def status(jids):
    jids = parse_jids(jids)
    cloud = _getcloud()
    statuses = cloud.status(jids)
    # encode answers with dct
    out_dct = OrderedDict(((jid, status) for jid, status in izip(jids.my_iter(), statuses)))
    return out_dct

def join(jids):
    jids = parse_jids(jids)
    cloud = _getcloud()
    return cloud.join(jids)    

class _JSON_String(str):
    json_encoded = True
    
    def __init__(self, contents):
        super(_JSON_String, self).__init__(contents)

def result(jids, timeout = None, ignore_errors = False): 
    jids = parse_jids(jids)
    cloud = _getcloud()
    results = cloud.result(jids, timeout, ignore_errors)
    result_dct = OrderedDict()
    for jid, result in izip(maybe_xrange_iter(jids), results):
        if isinstance(result, CloudException):
            result = 'CloudException: ' + str(result)
        if isinstance(result, basestring):
            pass
        elif isinstance(result, (int, bool, long, float)):
            pass # keep as primitive
        else:
            try:
                result = json.dumps(result)
            except (TypeError, UnicodeDecodeError):
                raise ValueError('Cannot view result of jid %s. It cannot be represented in JSON.' % jid)
            else:
                result = _JSON_String(result)
        result_dct[jid] = result
    return result_dct    

def info(jids, info_requested = None):
    jids = parse_jids(jids)
    if info_requested:
        info_requested = info_requested.split(',')
    cloud = _getcloud()
    return cloud.info(jids, info_requested)    

def kill(jids):
    jids = parse_jids(jids)
    cloud = _getcloud()
    return cloud.kill(jids)    

def delete(jids):
    jids = parse_jids(jids)
    cloud = _getcloud()
    return cloud.delete(jids)    

def parse_jids(jid_str):
    """Parse jid a-b,c format (same as used for rest"""        
        
    ujids = PiecewiseXrange() 
    try:
        for jid in jid_str.split(','):
            if '-' in jid:
                min_jid, max_jid = jid.split('-')
                ujids.append(xrange(int(min_jid), int(max_jid)+1))
            else:
                ujids.append(int(jid))
    except ValueError:
        raise ValueError("jids must be integers sperated by '-' or ','")
    ujids.to_xrange_mode()
    return ujids
