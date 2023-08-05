#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

try:
    import json
except ImportError:
    import simplejson as json

import codecs
import copy
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import types

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
log = logging.getLogger('projectmill')

MSS_VAR_RE = re.compile('^@([\w-]+):([\W]?[^;]+);$')


def merge_config(merge_left, merge_right):
    """Recursively merge two config dicts, returning a new dict as the result.

    The base of the merge is `merge_left`, and the values to merge in are taken
    recursively from `merge_right`. Both inputs are left unmodified by the
    process, and the result is a new dictionary.

    The behaviour is a little specialised, as if `merge_left` and `merge_right`
    are lists, we assume they are of equal length, and attempt merges on the
    pairs of elements in order.

    """
    if isinstance(merge_right, list):
        assert isinstance(merge_left, list)
        assert len(merge_left) == len(merge_right)
        result = []
        for l, r in zip(merge_left, merge_right):
            result.append(merge_config(l, r))
        return result

    if not isinstance(merge_right, dict):
        return merge_right

    result = copy.deepcopy(merge_left)
    for k, v in merge_right.items():
        if k in result and isinstance(result[k], (dict, list)):
            result[k] = merge_config(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result


def process_mml(sourcefile, config):
    """Merge base + custom configurations"""
    source_dict = dict()
    with codecs.open(sourcefile, 'r', 'utf-8') as f:
        source_dict = json.loads(f.read())

    assert isinstance(source_dict, dict), (
        "Base of config merges must be a dictionary: %s" % str(source_dict)
    )

    assert 'mml' in config

    return json.dumps(merge_config(source_dict, config.get('mml')), indent=2)


def process_mss(sourcefile, config):
    """Read the MSS file line by line & substitute out variables from config"""
    with codecs.open(sourcefile, 'r', 'utf-8') as f:
        in_lines = f.read().splitlines()

    subs = config.get('cartoVars')

    out_lines = []
    for line in in_lines:
        match = MSS_VAR_RE.search(line)
        if match:
            var_name, orig_value = match.groups()
            if var_name in subs:
                line = '@%s: %s;' % (var_name, subs.get(var_name, orig_value))

        out_lines.append(line)

    return '\n'.join(out_lines)


def mill(config):
    """Create new tilemill projects by merging configs."""
    for fname in os.listdir(config.get('source')):
        try:
            destfile = os.path.join(config.get('destination'), fname)
            destdir = os.path.dirname(destfile)
            sourcefile = os.path.join(config.get('source'), fname)

            if not os.path.exists(destdir):
                os.mkdir(destdir)

            if os.path.islink(sourcefile):
                # Symlinks are just reproduced
                os.symlink(os.path.realpath(sourcefile), destfile)
            elif 'mml' in config and fname == 'project.mml':
                # project.mml files are recursively merged with config before
                # copying
                with open(destfile, 'w') as f:
                    f.write(process_mml(sourcefile, config))
            elif 'cartoVars' in config and fname.endswith('.mss'):
                # map stylesheets have variables substituted from config before
                # copying
                with open(destfile, 'w') as f:
                    f.write(process_mss(sourcefile, config))
            else:
                # everything else, we just copy as-is
                if os.path.isfile(sourcefile):
                    shutil.copy(sourcefile, destfile)
                else:
                    shutil.copytree(sourcefile, destfile)

        except Exception:
            _, ex, _ = sys.exc_info()
            log.exception(
                'Error processing project: %s (%s)' %
                (config.get('destination'), ex)
            )
    log.info('Created project: %s' % config.get('destination'))


def render(key, config, dest, node_path, tilemill_path):
    """Call out to tilemill to render."""
    args = [
        'nice', '-n19', node_path, tilemill_path, 'export', key, dest,
        '--format=%s' % config.get('format'),
    ]
    for x in ['bbox', 'width', 'height', 'minzoom', 'maxzoom']:
        val = config.get(x)
        if val:
            args.append('--%s=%s' % (x, val))
    log.info('Spawning %s' % ' '.join(args))

    ret = subprocess.call(args)
    if ret:
        log.warn('Render failed for %s' % key)
    else:
        log.info('Rendered %s as %s' % (key, config.get('format')))

    # If this isn't mbtiles or we don't have any metadata to add, we're done
    if config.get('format') != 'mbtiles' or not config.get('MBmeta'):
        return

    conn = sqlite3.connect(dest)
    try:
        for k, v in config.get('MBmeta').items():
            assert isinstance(k, types.StringTypes)

            with conn:
                conn.execute(
                    'REPLACE INTO metadata (name, value) VALUES (?, ?)', (k, v)
                )
    except Exception:
        _, ex, _ = sys.exc_info()
        log.warn("sqlite operation failed for %s: %s" % (key, str(ex)))
    finally:
        conn.close()
