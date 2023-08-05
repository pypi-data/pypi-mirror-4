"""
PiCloud volume management.
This module allows the user to manage their volumes on PiCloud.
See documentation at http://docs.picloud.com

Be advised that you must have rsync installed for this module to work
"""
from __future__ import absolute_import
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
try:
    import json
except:
    # Python 2.5 compatibility
    import simplejson as json
import logging
import os
import platform
import re
import sys
import time
from datetime import datetime
from subprocess import Popen, PIPE

import cloud
from .cloudlog import stdout as print_stdout, stderr as print_stderr, verbose
from .util import credentials

cloudLog = logging.getLogger('Cloud.volume')

plat = platform.system()

_urls = {'list': 'volume/list/',
         'create': 'volume/create/',
         'mkdir': 'volume/mkdir/',
         'sync_initiate': 'volume/sync_initiate/',
         'sync_terminate': 'volume/sync_terminate/',
         'delete': 'volume/delete/',
         'check_release': 'volume/check_release/',
         'ls': 'volume/ls/',
         'rm': 'volume/rm/'
         }

_volume_path_delimiter = ':'

_SYNC_READY = 'ready'
_SYNC_NOVACANCY = 'novacancy'
_SYNC_ERROR = 'error'

_RELEASE_DONE = 'done'
_RELEASE_IN_PROGRESS = 'waiting'
_RELEASE_ERROR = 'error'

def _fix_time_element(dct, keys):
    if not hasattr(keys, '__iter__'):
        keys = [keys]

    FORMAT = '%Y-%m-%d %H:%M:%S'
    for key in keys:
        if dct.has_key(key):
            val = dct.get(key)
            dct[key] = None if (val == 'None') else datetime.strptime(val, FORMAT)

    return dct

def _send_request(request_type, data, jsonize_values=True):
    """Makes a cloud request and returns the results.  *request_type* indicates
    which request is being made, and *data* is a dictionary of post values
    relevant to the request.  If *jsonize_values* is True (default), then the
    values of the *data* dictionary are jsonized before request is made."""
    type_url = _urls.get(request_type)
    if not type_url:
        raise LookupError('Invalid request type %s' % request_type)
    if jsonize_values:
        data = _jsonize_values(data)
    conn = cloud._getcloudnetconnection()
    return conn.send_request(type_url, data)

def _jsonize_values(dct):
    """Jsonizes the values of the dictionary, but not the keys."""
    jsonized = [(key, json.dumps(value)) for key, value in dct.items()]
    jsonized.append(('_jsonized', True))
    return dict(jsonized)


"""
volume management
"""
def get_list(name=None, desc=False):
    """Returns a list of dictionaries describing user's volumes.
    If *name* is specified, only shows info for the volume with that name.
    If *desc* is True (default=False), then the description is also displayed.

    Volume information is returned as list of dictionaries.  The keys within
    each returned dictionary are:

    * name:
        name of the volume
    * desc:
        description of the volume (if desc option is True)
    * mnt_path:
        filesystem path where volume contents can be accessed by a job
    * created:
        time when the volume was created
    """
    v_list = _send_request('list', {'name': name, 'desc': desc})
    return [_fix_time_element(v, 'created') for v in v_list['volumes']]

def create(name, mount_path, desc=None):
    """Creates a new cloud volume.
        * name:
            name of the new volume (max 64 chars)
        * mount_path:
            absolute path where this volume will be mounted when jobs are run
            specifying access to this volume, i.e. mount point where jobs can
            access the contents of this volume.
        * desc:
            (optional) description of the volume (max 1024 chars)
    """
    if len(name) < 2:
        raise cloud.CloudException('Volume name must be at least 2 characters.')
    _send_request('create',
                  {'name': name, 'mnt_path': mount_path, 'desc': desc or ''})
    cloudLog.debug('created volume %s', name)

def mkdir(volume_path, parents=False):
    """Creates directory(ies) at volume_path, if they don't already exist.

    * volume_path:
        A cloud volume path spec or a list of specs, that indicates the
        directory(ies) to create.
    * parents:
        If True, does not error if the directory already exists, and makes any
        necessary parent directories.
    """
    vol_name, vol_paths = parse_volume_paths(volume_path)
    res = _send_request('mkdir',
                        {'name': vol_name, 'paths': vol_paths,
                         'parents': parents})

    if res.get('modified'):
        _wait_for_release(vol_name)
    msg = 'created %s in volume %s' % (', '.join(vol_paths), vol_name)
    cloudLog.debug(msg)
    print_stdout(msg)

def sync(source, dest):
    """Syncs data between a cloud volumes and the local filesystem.

    Either *source* or *dest* should specify a cloud volume path, but not both.
    A cloud volume path is of the format:

        volume_name:[path-within-volume]

    where path-within-volume cannot be an absolute path (There is no concept of
    the root of the filesystem in a volume: All path specifications are relative
    to the top level of the volume).  Note that the colon is what indicates this
    is a volume path specification.  Local paths should point to a local
    directory or file.  If the local path is a directory, whether the
    directory itself or the contents of the directory are synced depends on the
    presence of a trailing slash.  A trailing slash indicates that the contents
    should be synced, while its absence would lead to the directory itself being
    synced to the volume.  *source* can be a list of paths, all of which should
    either be local paths, or volume paths in the same cloud volume.

    Example::

        sync('~/dataset1', 'myvolume1:')

    will ensure that a directory named 'dataset1' will exist at the top level
    of the cloud volume 'myvolume1', that contains all the contents of
    'dataset1'.  On the other hand,

        sync('~/dataset1/', 'myvolume1:')

    will copy all the contents of 'dataset1' to the top level of 'myvolume1'.
    This behavior mirrors the file-copying tool 'rsync'.
    
    The sync will not delete files that exist in *dest* but not in *source*.
    """
    _check_dependencies()

    dest_is_local = is_local_path(dest)
    l_paths, r_paths = (dest, source) if dest_is_local else (source, dest)
    local_paths = parse_local_paths(l_paths)
    vol_name, vol_paths = parse_volume_paths(r_paths)
    
    # acquire syncslot and syncserver info to complete the real remote paths
    success = release = False
    exit_code = 1
    syncserver, syncslot = _acquire_syncslot(vol_name)

    try:
        cloudLog.debug('Acquired syncslot %s on server %s', syncslot, syncserver)
        r_base = '%s@%s:volume/' % (syncslot, syncserver)
        r_paths = ' '.join(['%s%s' % (r_base, v_path) for v_path in vol_paths])
        l_paths = ' '.join(local_paths)
        sync_args = (r_paths, l_paths) if dest_is_local else (l_paths, r_paths)
        exit_code, stdout, stderr = _perform_sync(*sync_args)
    except KeyboardInterrupt:
        cloudLog.error('Sync interrupted by keyboard')
        print 'Sync interrupted by keyboard'
    except Exception as e:
        cloudLog.error('Sync errored with:\n%s', e)
        print e
    else:
        if exit_code:
            cloudLog.error('rsync errored with:\n%s\n%s', stdout, stderr)
            print stderr
    finally:
        print_stdout('Cleanup...')
        success = not exit_code
        release = success and not dest_is_local
        _send_request('sync_terminate', {'name': vol_name,
                                         'syncslot': syncslot,
                                         'syncserver': syncserver,
                                         'release': release})

    if release:
        print_stdout('Ensuring redundancy...')
        _wait_for_release(vol_name)
    if success:
        print_stdout('Sync successfully completed.')

def delete(name):
    """Deletes the picloud volume identified by *name*."""
    _send_request('delete', {'name': name})
    cloudLog.debug('deleted volume %s', name)

def ls(volume_path, extended_info=False):
    """Lists the contents at *volume_path*.
    
    * volume_path:
        A cloud volume path spec or a list of specs, whose contents are to be
        returned.
    * extended_info:
        If True, in addition to the names of files and directories comprising
        the contents of the volume_path, the size (in bytes) and the modified
        times are returned. (Default is False)
    
    Returns a list of tuples, one for each volume path specified.  The first
    element of the tuple is the volume path spec, and the second element of the
    tuple is a list of dictionaries for each file or directory present in the
    volume path.
    """
    vol_name, vol_paths = parse_volume_paths(volume_path)
    res = _send_request('ls',
                        {'name': vol_name, 'paths': vol_paths,
                         'extended_info': extended_info})

    fixed_listings = []
    for v_path, listings in res.get('listings'):
        v_path = '%s:%s' % (vol_name, v_path)
        if extended_info:
            listings = [_fix_time_element(v, 'modified') for v in listings]
        fixed_listings.append((v_path, listings))

    return fixed_listings

def rm(volume_path, recursive=False):
    """Removes contents at *volume_path*.
    
    * volume_path:
        A cloud volume path spec or a list of specs, whose contents are to be
        removed.
    * recursive:
        If True, will remove the contents at *volume_path* recursively, if it
        is a directory.  If *recursive* is False, and *volume_path* points to
        a non-empty directory, it is an error. (Default is False)
    """
    vol_name, vol_paths = parse_volume_paths(volume_path)

    res = _send_request('rm',
                        {'name': vol_name,
                         'paths': vol_paths,
                         'recursive': recursive})
    if res.get('modified'):
        _wait_for_release(vol_name)
    cloudLog.debug('removed %s from volume %s', ', '.join(vol_paths), vol_name)

def is_local_path(path):
    return ((_volume_path_delimiter not in path) or
            (plat == 'Windows' and re.match(r'[a-zA-Z]:(\\|/)', path)))

def parse_local_paths(local_paths):
    """Validate local paths."""
    if not isinstance(local_paths, (tuple, list)):
        local_paths = [local_paths]
    
    parsed_paths = []
    for path in local_paths:
        if plat == 'Windows':
            path = str(WindowsPath(path))
        if path.count(_volume_path_delimiter):
            raise cloud.CloudException('Local path cannot contain ":"')
        parsed_paths.append(path)
    return parsed_paths

def parse_volume_paths(remote_paths):
    """Validate remote paths."""
    if not isinstance(remote_paths, (tuple, list)):
        remote_paths = [remote_paths]
    
    volume_name = None
    parsed_paths = []
    for path in remote_paths:
        if path.count(_volume_path_delimiter) != 1:
            raise cloud.CloudException('Volume path must be volume_name:path')
        vname, vol_path = path.split(_volume_path_delimiter)
        volume_name = volume_name or vname
        if not vname:
            raise cloud.CloudException('Volume path must start with a volume name')
        if volume_name != vname:
            raise cloud.CloudException('All volume paths must use the same volume')
        if os.path.isabs(vol_path):
            raise cloud.CloudException('Volume path cannot be absolute')
        parsed_paths.append(vol_path)
    return (volume_name, parsed_paths)

def _acquire_syncslot(volume_name):
    """Requests syncslot from PiCloud.  Current behavior is to try 12 times,
    waiting 5 seconds between failed attempts."""
    num_retries = 12
    wait_time = 5   # seconds
    print_stdout('Connecting with PiCloud to initiate sync', False)
    while num_retries:
        print_stdout('.', False)
        res = _send_request('sync_initiate', {'name': volume_name})
        status = res.get('status')
        if status == _SYNC_NOVACANCY:
            num_retries -= 1
            time.sleep(wait_time)
            continue
        if status not in [_SYNC_READY, _SYNC_ERROR]:
            status = _SYNC_ERROR
        break
    print_stdout('')
    
    if status == _SYNC_NOVACANCY:
        cloudLog.error('No available syncslot')
        raise cloud.CloudException('Volume sync is unavailable at the moment.  '
                                   'Please try again in a few minutes.  '
                                   'We Apologize for the inconvenience.')
    if status == _SYNC_ERROR:
        cloudLog.error('Error acquiring syncslot')
        raise cloud.CloudException('Could not complete volume sync.  '
                                   'Please contact PiCloud support.')

    return res.get('syncserver'), res.get('syncslot')

def _rsync_path():
    base_dir = os.path.join(sys.prefix, 'extras') if plat == 'Windows' else ''
    return os.path.join(base_dir, 'rsync')

def _ssh_path():
    base_dir = os.path.join(sys.prefix, 'extras') if plat == 'Windows' else ''
    return os.path.join(base_dir, 'ssh')

def _check_dependencies():
    """Checks dependencies by trying the commands."""
    msg_template = 'Dependency %s not found'
    if plat == 'Windows':
        msg_template += ' in cloud installation'

    # check rsync exists
    status, _, _ = _exec_command('%s --version' % _rsync_path())
    if status:
        raise cloud.CloudException(msg_template % 'rsync')
    
    # check ssh exists
    status, _, _ = _exec_command('%s -V' % _ssh_path())
    if status:
        raise cloud.CloudException(msg_template % 'ssh')

def _perform_sync(src_arg, dest_arg):
    """Perform a sync operation over ssh using api_key's ssh key."""
    api_key = cloud.connection_info().get('api_key')
    key_file = credentials.get_sshkey_path(api_key)
    ssh_path = _ssh_path()
    rsync_path = _rsync_path()
    if plat == 'Windows':
        key_file = str(WindowsPath(key_file))
        ssh_shell = ('%s -q -o StrictHostKeyChecking=no -i %s' %
                     (ssh_path, key_file))
    else:
        ssh_shell = ('%s -q -o UserKnownHostsFile=/dev/null '
                     '-o StrictHostKeyChecking=no -i %s' %
                     (ssh_path, key_file))

    cmd = '%s -avze "%s" %s %s' % (rsync_path, ssh_shell, src_arg, dest_arg)
    cloudLog.debug('Performing sync command: %s', cmd)
    print_stdout('Performing sync...')
    pipe_output = not verbose
    return _exec_command(cmd, pipe_output)

def _wait_for_release(volume_name, wait_interval=3):
    """Polls volume's status until it's no longer waiting release."""
    while True:
        res = _send_request('check_release', {'name': volume_name})
        status = res['status']
        if status == _RELEASE_ERROR:
            raise cloud.CloudException('Sync failed on volume %s' % volume_name)
        if status == _RELEASE_DONE:
            break
        time.sleep(3)

def _exec_command(cmd, pipe_output=True):
    """Simple shell exec wrapper, with no stdin."""
    if pipe_output:
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    else:
        p = Popen(cmd, shell=True)
    stdout, stderr = p.communicate()
    status = p.returncode
    return (status, stdout, stderr)

class WindowsPath(object):
    """Processes Windows paths for easy conversion into cwRsync compatible
    format.  This involves replacing drive specification into
    /cygdrive/[drive_lettter] format, and replacing backward slashes with
    forward slashes.  While backward slashes will allow correctly locating the
    filesystem resource locally, it most likely will result in incorrect
    destinations on the remote side, as backward slashes will be interpreted as
    part of the name itself.
    """
    def __init__(self, path):
        """Path is any (absolute or relative) Windows path."""
        if os.path.isabs(path):
            drive, tail = os.path.splitdrive(path)
            self.drive = drive.rstrip(':')
            self.tail = tail.lstrip('\\').lstrip('/')
        else:
            self.drive = ''
            self.tail = path.lstrip('\\').lstrip('/')

    def __repr__(self):
        """This is where the rsync safe conversion takes place.  If there is a
        space in the path, encapsulates the path with quotes to assure the path
        will not be misinterpreted as being two or more paths.
        """
        drive = os.path.join('\\cygdrive', self.drive) if self.drive else ''
        path = os.path.join(drive, self.tail)
        path = path.replace('\\', '/')
        if " " in path:
            path = '"%s"' % path
        return path
