"""
Queues provide an interface for flow-based programming on PiCloud.

Please see our `Queue documentation <http://docs.picloud.com/queue.html>`_.
"""

from __future__ import with_statement
from __future__ import absolute_import
"""
Copyright (c) 2013 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

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

"""Dev beware: list is defined in this module; list will not map to builtin list. Use builtin_list instead"""

import sys
import json
import time
import errno
import os
import random
import base64
import socket
import string
import urllib2
from itertools import izip

from Queue import Queue as FIFO
import traceback
import threading

from functools import wraps
from .serialization import cloudpickle as pickle


__httpConnection = None
__url = None

from .util import  min_args, max_args
from .util.zip_packer import Packer
from .cloud import CloudException 
from . import _getcloudnetconnection, _getcloud


import logging
cloudLog = logging.getLogger('Cloud.queue')

_queue_create_query = 'queue/'
_queue_list_query = 'queue/'
_queue_count_query = 'queue/{name}/count/'
_queue_exists_query = 'queue/{name}/exists/'
_queue_info_query = 'queue/{name}/'
_queue_delete_query = 'queue/{name}/delete/'
_queue_messages_push_query = 'queue/{name}/push/'
_queue_messages_pop_query = 'queue/{name}/pop/'
_queue_attach_query = 'queue/{name}/attach/'
_queue_detach_query = 'queue/{name}/detach/'

# maximum number of messages to push in a single push
_queue_push_limit = 800

"""
The functions can be viewed as functionally close to instance methods of cloud.Cloud
"""

def _post(conn, url, post_values, headers={}):
    """Use HttpConnection *conn* to issue a post request at *url* with values *post_values*"""
    
    #remove UNICODE from addresses
    url = url.decode('ascii', 'replace').encode('ascii', 'replace')
    
    if 'success_action_redirect' in headers:
        headers['success_action_redirect'] = headers['success_action_redirect'].decode('ascii', 'replace').encode('ascii', 'replace')
    if post_values and 'success_action_redirect' in post_values:
        post_values['success_action_redirect'] = post_values['success_action_redirect'].decode('ascii', 'replace').encode('ascii', 'replace')
    
    cloudLog.debug('post url %s with post_values=%s. headers=%s' % (url, post_values, headers))
    response =  conn.post(url, post_values, headers, use_gzip=False)
    
    return response


def list():
    """Returns a list of all queues that are registered on PiCloud.
    
    Note that registration is lazy; see get()
    """

    conn = _getcloudnetconnection()
    
    resp = conn.send_request(_queue_list_query, None)

    return resp['queues']


def get(name):
    """
    Return cloud Queue object named ``name``
    
    Note that the Queue named ``name`` is lazily created (appearing in list) on PiCloud.
    Until an operation with a queue object named ``name`` is executed, ``exists(name)`` will return False
    """
    
    return Queue(name)

def exists(name):
    """Returns True if a queue of ``name`` 
    has already been created on PiCloud
    """
    
    conn = _getcloudnetconnection()
    
    resp = conn.send_request(_queue_exists_query.format(name=name), None)
    
    return resp['exists']


class Queue(object):
    """
    A Queue that is distributed across PiCloud
    Any instantiated Queue with the same ``name`` will share state.
    That is if one machine pushes data to a Queue with name 'q', any
    other machine can pop data from a Queue with name 'q'
    """
    
    # Name of this Queue object
    name = None
    
    def __init__(self, name):
        """
        See docs for get()        
        """
        valid_chars_in_name = string.letters + string.digits + '-_'
        
        for c in name:
            if c not in valid_chars_in_name:
                raise ValueError('name must only container alphanumeric, '
                                 'underscore, or hyphen characters')
                
        if len(name) >= 40:
            raise ValueError('Length of name exceeded max of 40 characters (got %s)' % len(name))
        
        self.name = name

    def count(self):
        """Returns an approximation of the number of messages in the queue."""
    
        conn = _getcloudnetconnection()
        
        resp = conn.send_request(_queue_count_query.format(name=self.name), None)
    
        return resp['count']
    
    def info(self):
        """Returns a dictionary describing the queue (notably attachment information)"""
    
        conn = _getcloudnetconnection()
        
        resp = conn.send_request(_queue_info_query.format(name=self.name), None)
    
        return resp['info']
    
    def delete(self):
        """Delete all of queue's contents and remove it from PiCloud"""
    
        conn = _getcloudnetconnection()
        
        resp = conn.send_request(_queue_delete_query.format(name=self.name), None)
    
        return True
    
    def detach(self):
        """Detaches any attached message handler"""
    
        conn = _getcloudnetconnection()
        
        resp = conn.send_request(_queue_detach_query.format(name=self.name), None)
    
        return True
    
    def _encode_message(self, message):
        try:                
            serialized_message = json.dumps(message)                
            datatype = 'json'
            json_dct = {'message' : serialized_message,
                        'datatype' : datatype}
            
        except (TypeError, UnicodeDecodeError): # errors json.dumps may raise
            try:
                serialized_message = pickle.dumps(message, 2)
                datatype = 'base64_python_pickle'
                
                # only even try to encode if small enough
                if len(serialized_message) < 64000:
                    json_dct = {'datatype': datatype, 'message': base64.b64encode(serialized_message)}
                else:
                    json_dct = None
            except:
                cloudLog.exception('Could not pickle message')
                raise

        if json_dct:
            encoded_message = json.dumps(json_dct)
        
        if not json_dct or len(encoded_message) > 64000:
            from . import bucket
            import uuid
            obj_key = 'queue/{name}/{uuid}'.format(name=self.name, uuid=uuid.uuid4())
            bucket.putf(serialized_message, obj_key)
            if datatype == 'base64_python_pickle':
                datatype = 'python_pickle'
            encoded_message = json.dumps({'datatype': datatype, 'redirect': 'bucket', 'key': obj_key})
        
        return encoded_message        
    
    def push(self, messages, delay=0):
        """Put *messages*, a list of objects, into queue. If *delay*
        is specified, the function will return immediately, but the messages
        will not be available to readers (poppers) for *delay* seconds.
    
        Each object in *messages* must be pickle-able
        
        Note that if the picked message exceeds 64kb, it will be temporarily saved 
        to your cloud.bucket under the queue/ prefix
        """
        
        if not isinstance(delay, (int, long)):
            raise TypeError('delay must be an integer')
        
        if not 900 >= delay >= 0:
            raise ValueError('delay must be between 0 and 900 seconds inclusive.')
        
        if not hasattr(messages, '__iter__'):
            raise ValueError('messages must be an iterable') 

        encoded_messages = []
        cnt = 0
        for message in messages:
            cnt+=1
            encoded_messages.append(self._encode_message(message))
            if cnt >= _queue_push_limit:
                self._low_level_push(encoded_messages, delay)
                encoded_messages = []
                cnt = 0
        if encoded_messages:
            self._low_level_push(encoded_messages, delay)
        return True
    
    def _low_level_push(self, encoded_messages, delay=0):
        """push encoded messages (see push)"""
        conn = _getcloudnetconnection()
        resp = conn.send_request(_queue_messages_push_query.format(name=self.name), 
                         {'message': encoded_messages, 'delay': delay})
        return True
    
    def _decode_message(self,encoded_message):
        from . import bucket    
        
        if isinstance(encoded_message, basestring):
            message_data = json.loads(encoded_message)
        elif isinstance(encoded_message, dict):
            message_data = encoded_message
        else:
            raise TypeError('encoded_message must be a json string or dictionary')
            
        if isinstance(message_data, dict) and message_data.get('datatype'):
            
            redirect = message_data.get('redirect')
            datatype = message_data.get('datatype')
            
            if redirect and redirect == 'bucket':
                redirect_key = message_data['key']
                message_payload = bucket.getf(redirect_key).read()
                bucket.remove(redirect_key)
            elif redirect:
                raise RuntimeError('Do not understand redirect %s' % redirect)
            else:
                message_payload = message_data['message']
                
            if datatype == 'python_pickle':
                return pickle.loads(message_payload)
            elif datatype == 'base64_python_pickle':
                return pickle.loads(base64.b64decode(message_payload))
            elif datatype == 'json':
                return json.loads(message_payload)
            else:
                raise Exception('Unknown datatype %s' % datatype)
                        
        else:
            return message_data    
    
    
    def _low_level_pop(self, max_count, timeout):
        """pops a list of json encoded messages"""
        
        conn = _getcloudnetconnection()
    
        resp = conn.send_request(_queue_messages_pop_query.format(name=self.name), 
                                 {'max_count': max_count, 'timeout': timeout})
    
        return resp['messages']
        
    
    def pop(self, max_count=10, timeout=20):
        """Pops at most *max_count* messages from the queue. Returns a list of messages popped
        
        Blocks until at least one message is available.
        
        If after ``timeout`` seconds, there are no messages, return empty list
    
        *timeout* must be specified as an integer between 0 and 20 inclusive.
        *max_count* must be specified as an integer between 1 and 10 inclusive."""
    
        if not isinstance(max_count, (int, long)):
            raise TypeError('max_count must be an integer')
        if not isinstance(timeout, (int, long)):
            raise TypeError('timeout must be an integer')
        
        if not (10 >= max_count > 0):
            raise ValueError('max_count must be between 1 and 10 inclusive')
    
        if not (20 >= timeout >= 0):
            raise ValueError('timeout must be between 0 and 20 inclusive')
        
        results_data = self._low_level_pop(max_count, timeout)
        
        messages = []
        
        from . import running_on_cloud
        
        for datum in results_data:
            try:
                messages.append(self._decode_message(datum))
            except:
                cloudLog.exception('Could not decode a message')
                if running_on_cloud():
                    sys.stderr.write('Could not decode a message.\n')
                    traceback.print_exc()
                    sys.stderr.write('\n')
                else:
                    raise
                
        return messages

    
    def attach(self, message_handler, output_queues=[],  
               readers_per_job=1, max_parallel_jobs=1, **kwargs):
        
        """Register *message_handler* as the processor for this queue on PiCloud.
        
        If ``message_handler`` is a function (or any callable), then it will be
        invoked for each message, with the message as the only argument.
        
        The queue processing will occur in the context of a job. The job automatically
        completes if no data is available in the queue for 20 seconds.
        
        Alternatively, ``message_handler`` may be an instance if it is desired to maintain state 
        between message processing. In this case, the mssage_handler function will be the 
        instance's method "message_handler()" which takes a single argument (a message).        
        The instance may optionally provide ``pre_handling`` and ``post_handling`` methods to manage
        startup and cleanup respectively. ``pre_handling`` is called once before the first 
        message is processed by the wrapping job, and ``post_handling`` is called once after the last
        message is processed by the wrapping job.  
        
        If the return value of message handler is not ``None``, result will be pushed to each queue in 
        ``output_queues``
        
        ``readers_per_job controls`` the number of messages can be processed by a job in parallel.
        
        ``max_parallel_jobs`` is the maximum number of jobs that can run in parallel to process your queue
        
        Certain special *kwargs* associated with cloud.call can be used for your *message_handler*: 
        
        * _cores:
            Set number of cores your job will utilize. See http://docs.picloud.com/primer.html#choose-a-core-type/
            In addition to having access to more CPU cores, the amount of RAM available will grow linearly.
            Possible values for ``_cores`` depend on what ``_type`` you choose:
            
            * c1: 1                    
            * c2: 1, 2, 4, 8
            * f2: 1, 2, 4, 8, 16                                    
            * m1: 1, 2
            * s1: 1        
        * _env:
            A string specifying a custom environment you wish to run your job within.
            See environments overview at http://docs.picloud.com/environment.html
        * _label: 
            A user-defined string label that is attached to the jobs. Labels can be
            used to filter when viewing jobs interactively (i.e. on the PiCloud website).                            
        * _priority: 
            A positive integer denoting the jobs' priority. PiCloud tries to run jobs 
            with lower priority numbers before jobs with higher priority numbers.                
        * _profile:
            Set this to True to enable profiling of your code. Profiling information is 
            valuable for debugging, and finding bottlenecks.
            **Warning**: Profiling can slow your job significantly; 10x slowdowns are known to occur
        * _restartable:
            In the rare event of hardware failure while a job is processing, this flag
            indicates whether the job can be restarted. By default, this is True. Jobs
            that modify external state (e.g. adding rows to a database) should set this
            False to avoid potentially duplicate modifications to external state.
        * _type:
            Choose the type of core to use, specified as a string:
            
            * c1: 1 compute unit, 300 MB ram, low I/O (default)                    
            * c2: 2.5 compute units, 800 MB ram, medium I/O
            * f2: 5.5 compute units, 3.75 GB ram, high I/O, hyperthreaded core                                    
            * m1: 3.25 compute units, 8 GB ram, high I/O
            * s1: Up to 2 compute units (variable), 300 MB ram, low I/O, 1 IP per core
                           
            See http://www.picloud.com/pricing/ for pricing information
        * _vol:
            A string or list of strings specifying a volume(s) you wish your jobs to have access to. 
                     
        """
        
        # TODO: Bring back batch_size to the public API
        
        cloud = _getcloud()
        params = cloud._getJobParameters(message_handler, kwargs, 
                                         ignore=['_depends_on', '_depends_on_errors', 
                                                 '_max_runtime', '_fast_serialization',
                                                 '_kill_process'])
        
        return _low_level_attach(self, message_handler, False, output_queues, None, 
                                 readers_per_job, max_parallel_jobs, params)
    


    def attach_generator(self, message_handler, output_queues=[], readers_per_job=1, 
                         max_parallel_jobs=1, **kwargs):
        """Same as *attach*, except message_handler will return an iterator 
        (generator, list, etc.)
        
        Each value from the iterator will be treated as a separate message and
        added to each of the *output_queues*.
        
        (if a value of None is yielded, it will be treated as a message unlike with *attach*)
        """
        
        cloud = _getcloud()
        params = cloud._getJobParameters(message_handler, kwargs, 
                                         ignore=['_depends_on', '_depends_on_errors', 
                                                 '_max_runtime', '_fast_serialization',
                                                 '_kill_process'])
        
        return _low_level_attach(self, message_handler, True, output_queues, None, 
                                 readers_per_job, max_parallel_jobs, params)

    def __repr__(self):
        return "CloudQueue('{name}')".format(name=self.name)


def _low_level_attach(queue, message_handler, expand_iterable_output, output_queues, 
                      batch_size, readers_per_job, max_parallel_jobs, params):
    """Does the grunt work in attaching the *message_handler* to the queue."""

    if not isinstance(readers_per_job, (int, long)):
            raise TypeError('readers_per_job must be an integer')
    if not isinstance(max_parallel_jobs, (int, long)):
        raise TypeError('timeout must be an integer')
        
    if not (max_parallel_jobs >= 1):
        raise ValueError('max_parallel_jobs must be greater than 0')
    
    if not (128 >= readers_per_job >= 1):
        raise ValueError('readers_per_job must be between 1 and 128 inclusive')


    if output_queues:
        if not hasattr(output_queues, '__iter__'):
            output_queues = [output_queues]
        
        if len(output_queues) > 50:
            raise ValueError('Cannot specify more than 50 output queues.')
        
        for output_queue in output_queues:
            if not isinstance(output_queue, Queue):
                raise ValueError('output queues must be Queue instances')

    implements_interface = False

    if not callable(message_handler):
        # if obj has a message_handler member, it's all good
        # if obj has a message_handler member, but not callable, error
        # if obj doesn't have a message_handler member, error with callable needed
        
        if not hasattr(message_handler, 'message_handler'):
            raise TypeError('cloud.queue.attach *message_handler* argument (%s) is not callable'  % (str(message_handler)))
        
        elif not callable(getattr(message_handler, 'message_handler')):
            raise TypeError('cloud.queue.attach *message_handler* is class without (%s) callable message_handler() member function'  % (str(message_handler)))
        
        implements_interface = True
    
    # TODO: Determine appropriate batch_size
    # In theory, with more parallel jobs, lower batch size (heroku problem) 
    #  will likely need to make this adaptive
    if not batch_size:
        batch_size = 10  # maximum possible
    
    try:
        if implements_interface:
            min_arg = min_args(message_handler.message_handler)
            max_arg = max_args(message_handler.message_handler)
        else:
            min_arg = min_args(message_handler)
            max_arg = max_args(message_handler)
    except TypeError:
        pass #type can't be sanity checked.. let it through
    else:
        if max_arg < 1 or min_arg > 1:
            raise ValueError('message_handler function must accept 1 (required) argument. %s requires %s' \
                             % (str(message_handler), min_arg))
    
    attachment = _create_attachment(queue, message_handler, expand_iterable_output, output_queues, batch_size, readers_per_job)

    cloud = _getcloud()
    conn = _getcloudnetconnection()
    
    smessage_handler, sarg, logprefix, logcnt = cloud.adapter.cloud_serialize(attachment, 2, [],
                                                                   logprefix='queue.')
    
    conn._update_params(params)
    
    cloud.adapter.dep_snapshot()
    
    data = Packer()
    data.add(smessage_handler)
    params['data'] = data.finish()
    params['output_queue'] = [output_queue.name for output_queue in output_queues]
    params['batch_size'] = batch_size
    params['readers_per_job'] = readers_per_job
    params['max_parallel_jobs'] = max_parallel_jobs
    
    conn.send_request(_queue_attach_query.format(name=queue.name), params) 
    
# sentinel to indicate when queue is done
queue_sentinel = object()

def _create_attachment(input_queue, message_handler, expand_iterable_output, output_queues, 
                       batch_size, readers_per_job, _job_shutdown_timeout=20):
    """Creates the function to be executed on PiCloud."""

    def attachment_runner(message_queue, result_queue):

        message_handler_func =  message_handler if callable(message_handler) else message_handler.message_handler
        pre_handling_func = message_handler.pre_handling if callable(getattr(message_handler, 'pre_handling', None)) else None
        post_handling_func = message_handler.post_handling if callable(getattr(message_handler, 'post_handling', None)) else None
        sentinel = None
        
        if pre_handling_func:
            try:
                pre_handling_func()
            except:
                sys.stderr.write('pre_handling raised exception.\n')
                traceback.print_exc()
                sys.stderr.write('\n')
                sentinel = 'pre_handling errored:\n' + traceback.format_exc()

        while True:
            
            encoded_message = message_queue.get()
            
            if not encoded_message: # sentinel
                if post_handling_func:
                    try:
                        post_handling_func()
                    except:
                        sys.stderr.write('post_handling raised exception.\n')
                        traceback.print_exc()
                        sys.stderr.write('\n')
                        if not sentinel:
                            sentinel = 'post_handling errored:\n' + traceback.format_exc()
                
                result_queue.put(sentinel)
                break
            
            message = input_queue._decode_message(encoded_message)
            
            try:
                results = message_handler_func(message)
            except:
                sys.stderr.write('Attached function raised exception. Message ignored.\n')
                traceback.print_exc()
                sys.stderr.write('\n')
                if not sentinel:
                    sentinel = 'message_handler errored:\n' + traceback.format_exc()
            else:
                if not expand_iterable_output:
                    results = [results]
                    
                for result in results:
                    
                    # None indicates no message w/ standard attach
                    if not expand_iterable_output and result is None: 
                        continue
                    
                    # each queue uses a unique bucket reference, so must encode multiple times
                    # TODO: This could be optimized to use a single bucket reference for all output queues                    
                    encoded_results = [output_queue._encode_message(result) for output_queue in output_queues]
                
                    result_queue.put(encoded_results)
    
    def attachment():
        """Responsible for creating subprocesses, each of which will have
        run a reader that processes the input queue."""
        
        # Implemented with multiprocessing queue for very high throughput
        #  Downside is that we can have one message always buffered
        
        from multiprocessing import Process, Queue as MPQueue
        from multiprocessing.queues import Empty as QueueEmpty
        from multiprocessing.queues import Full as QueueFull
        
        message_queue = MPQueue(1) # inbound queue; limited size ensures only 1 message buffered (another job elsewhere may take it)
        result_queue = MPQueue(1000) # queue where results are written to
        
        all_processes = []
        for _ in xrange(readers_per_job):
            p = Process(target = attachment_runner, args=(message_queue, result_queue))
            p.start()
            all_processes.append(p)
            
        exception = [None] # list of one element so push_to_queue can modify it
                    
        def push_to_queue():
            """Run indefinitely, popping lists of messages off a queue,
            and pushing them to the output cloud queues."""
            
            max_items = 800 # maximum number of items to push to a queue in a single request
            
            sentinel_signals = 0
            
            while sentinel_signals < readers_per_job:
                                
                encoded_message_list = [result_queue.get()]
                dequeue_cnt = 1
                
                # flush queue for batching
                try:
                    while dequeue_cnt < max_items:
                        encoded_message_list.append(result_queue.get_nowait())
                        dequeue_cnt+=1 
                except QueueEmpty:
                    pass
                
                # extract sentinels
                sentinels = [encoded_message for encoded_message in encoded_message_list if not hasattr(encoded_message, '__iter__')]
                sentinel_signals += len(sentinels)
                if not exception[0]:
                    sentinel_errors = [sentinel for sentinel in sentinels if sentinel]
                    if len(sentinel_errors) > 0:
                        exception[0] = sentinel_errors[0]
                
                encoded_message_list = [encoded_message for encoded_message in encoded_message_list if hasattr(encoded_message, '__iter__')]
                                    
                # An encoded_message has 1 to 1 mapping to output queue it is encoded for
                #  If confused what is going on here, ask Aaron
                for output_queue, encoded_message in zip(output_queues, zip(*encoded_message_list)):
                    output_queue._low_level_push( encoded_message )
                    
        push_thread = threading.Thread(target=push_to_queue)
        push_thread.daemon = True
        push_thread.name = 'Output Queue Push Thread'
        push_thread.start()
        
        cloudLog = logging.getLogger('Cloud.queue')
        cloudLog.debug('All subprocesses started. Listening on queue')
        
        # Main thread processes the input queue
        while True:
            messages = input_queue._low_level_pop(batch_size, timeout=_job_shutdown_timeout)
            if not messages:  # shut down job
                break 
            
            try:
                for message in messages:
                    message_queue.put(message)
            except QueueFull: # on system exit, this may be raised; translate to a system exit
                raise SystemExit('Killed')
        
        # SHUTDOWN
        cloudLog.debug('No more messages in queue')
        
        # send sentinels
        for _ in xrange(readers_per_job):
            try:
                message_queue.put(None)
            except QueueFull: # on system exit, this may be raised; do not propagate
                raise SystemExit('Killed')
                

        # wait for all processes to get sentinel and terminate
        for p in all_processes:
            p.join()
        
        cloudLog.debug('Waiting for outputs to flush.')
                    
        push_thread.join() 
        
        cloudLog.debug('Done')
        
        if exception[0]:
            raise CloudException(exception[0])
        
    if callable(message_handler):
        return wraps(message_handler)(attachment)
    else:
        return wraps(message_handler.message_handler)(attachment)
