# -*- coding: utf-8 -*-
"""
    # shake-files.helpers
"""
import datetime
import errno
import os
import random
import re
import uuid

# Get the fastest json available
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError('Unable to find a JSON implementation')

from werkzeug.utils import secure_filename


def format_path(tmplpath, filename, now=None):
    """
    {yyyy},{yy}: Year
    {mm}, {m}: Month (0-padded or not)
    {ww}, {w}: Week number in the year (0-padded or not)
    {dd}, {d}: Day (0-padded or not)
    {hh}, {h}: Hours (0-padded or not)
    {nn}, {n}: Minutes (0-padded or not)
    {ss}, {s}: Seconds (0-padded or not)
    {a+}: Filename first letters
    {z+}: Filename last letters
    {r+}: Random letters and/or numbers
    
        >>> tmplpath = '{zzz}/{yyyy}/{a}/{a}/{a}'
        >>> filename = 'monkey.png'
        >>> now = datetime(2010, 1, 14)
        >>> format_path(tmplpath, filename, now)
        'png/2010/m/o/n/'
    
    """
    path = tmplpath.lower()
    filename = filename.lower()
    now = now or datetime.datetime.utcnow()
    srx = r'\{(y{4}|[ymdhnws]{1,2}|[azr]+)\}'
    rx = re.compile(srx, re.IGNORECASE)
    len_filename = len(filename)
    a_pos = 0
    z_pos = 0
    delta = 0
    for match in rx.finditer(path):
        pattern = match.groups()[0]
        len_pattern = len(pattern)
        replace = '%0' + str(len_pattern) + 'i'
        if pattern.startswith('y'):
            replace = str(now.year)
            replace = replace[-len_pattern:]
        elif pattern.startswith('m'):
            replace = replace % now.month
        elif pattern.startswith('w'):
            tt = now.timetuple()
            replace = '%0' + str(len_pattern) + 'i'
            week = (tt.tm_yday + 7 - tt.tm_wday) / 7 + 1
            replace = replace % week
        elif pattern.startswith('d'):
            replace = replace % now.day
        elif pattern.startswith('h'):
            replace = replace % now.hour
        elif pattern.startswith('n'):
            replace = replace % now.minute
        elif pattern.startswith('s'):
            replace = replace % now.second
        elif pattern.startswith('a'):
            if a_pos >= len_filename:
                replace = '_'
            else:
                new_a_pos = a_pos + len_pattern
                replace = filename[a_pos:new_a_pos]
                a_pos = new_a_pos
        elif pattern.startswith('z'):
            new_z_pos = z_pos + len_pattern
            if z_pos == 0:
                replace = filename[-new_z_pos:]
            else:
                replace = filename[-new_z_pos:-z_pos]
            z_pos = new_z_pos
        elif pattern.startswith('r'):
            allowed_chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
            replace = ''.join([random.choice(allowed_chars) \
                for i in range(len_pattern)])
        else:
            raise ValueError
        x, y = match.span()
        path = '%s%s%s' % (path[:x - delta], replace, path[y - delta:])
        delta += len_pattern + 2 - len(replace)
    if not path.endswith('/'):
        path += '/'
    return path


def get_random_filename():
    return str(uuid.uuid4())


def get_unique_filename(root_path, path, name, ext=''):
    """ """
    path = os.path.join(root_path, path)
    abspath = os.path.abspath(path)
    i = 0
    while True:
        if i:
            filename = '%s_%i' % (name, i)
            filename = secure_filename(filename)
        else:
            filename = secure_filename(name)
        
        if ext:
            filename = '%s.%s' % (filename, ext.strip('.'))
        filepath = os.path.join(abspath, filename)
        if not os.path.exists(filepath):
            break
        i += 1
    return filename


def make_dirs(root_path, filepath):
    fullpath = os.path.join(root_path, filepath)
    fullpath = os.path.abspath(fullpath)
    try:
        os.makedirs(fullpath)
    except (OSError), e:
        if e.errno != errno.EEXIST:
            raise
    return fullpath

