#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
via psutil
"""

import glob
import re
import collections
import os
import sys

POSIX = os.name == "posix"
_DEFAULT = object()
FILE_READ_BUFFER_SIZE = 32 * 1024
ENCODING = sys.getfilesystemencoding()
try:
    ENCODING_ERRS = sys.getfilesystemencodeerrors()  # py 3.6
except AttributeError:
    ENCODING_ERRS = "surrogateescape" if POSIX else "replace"


def open_text(fname):
    """On Python 3 opens a file in text mode by using fs encoding and
    a proper en/decoding errors handler.
    On Python 2 this is just an alias for open(name, 'rt').
    """
    # See:
    # https://github.com/giampaolo/psutil/issues/675
    # https://github.com/giampaolo/psutil/pull/733
    fobj = open(fname, buffering=FILE_READ_BUFFER_SIZE,
                encoding=ENCODING, errors=ENCODING_ERRS)
    try:
        # Dictates per-line read(2) buffer size. Defaults is 8k. See:
        # https://github.com/giampaolo/psutil/issues/2050#issuecomment-1013387546
        fobj._CHUNK_SIZE = FILE_READ_BUFFER_SIZE
    except AttributeError:
        pass
    except Exception:
        fobj.close()
        raise

    return fobj


def open_binary(fname):
    return open(fname, "rb", buffering=FILE_READ_BUFFER_SIZE)


def cat(fname, fallback=_DEFAULT, _open=open_text):
    """Read entire file content and return it as a string. File is
    opened in text mode. If specified, `fallback` is the value
    returned in case of error, either if the file does not exist or
    it can't be read().
    """
    if fallback is _DEFAULT:
        with _open(fname) as f:
            return f.read()
    else:
        try:
            with _open(fname) as f:
                return f.read()
        except (IOError, OSError):
            return fallback


def bcat(fname, fallback=_DEFAULT):
    """Same as above but opens file in binary mode."""
    return cat(fname, fallback=fallback, _open=open_binary)


def sensors_temperatures():
    """Return hardware (CPU and others) temperatures as a dict
    including hardware name, label, current, max and critical
    temperatures.

    Implementation notes:
    - /sys/class/hwmon looks like the most recent interface to
      retrieve this info, and this implementation relies on it
      only (old distros will probably use something else)
    - lm-sensors on Ubuntu 16.04 relies on /sys/class/hwmon
    - /sys/class/thermal/thermal_zone* is another one but it's more
      difficult to parse
    """
    ret = collections.defaultdict(list)
    basenames = glob.glob('/sys/class/hwmon/hwmon*/temp*_*')
    # CentOS has an intermediate /device directory:
    # https://github.com/giampaolo/psutil/issues/971
    # https://github.com/nicolargo/glances/issues/1060
    basenames.extend(glob.glob('/sys/class/hwmon/hwmon*/device/temp*_*'))
    basenames = sorted(set([x.split('_')[0] for x in basenames]))

    # Only add the coretemp hwmon entries if they're not already in
    # /sys/class/hwmon/
    # https://github.com/giampaolo/psutil/issues/1708
    # https://github.com/giampaolo/psutil/pull/1648
    basenames2 = glob.glob(
        '/sys/devices/platform/coretemp.*/hwmon/hwmon*/temp*_*')
    repl = re.compile('/sys/devices/platform/coretemp.*/hwmon/')
    for name in basenames2:
        altname = repl.sub('/sys/class/hwmon/', name)
        if altname not in basenames:
            basenames.append(name)

    for base in basenames:
        try:
            path = base + '_input'
            current = float(bcat(path)) / 1000.0
            path = os.path.join(os.path.dirname(base), 'name')
            unit_name = cat(path).strip()
        except (IOError, OSError, ValueError):
            # A lot of things can go wrong here, so let's just skip the
            # whole entry. Sure thing is Linux's /sys/class/hwmon really
            # is a stinky broken mess.
            # https://github.com/giampaolo/psutil/issues/1009
            # https://github.com/giampaolo/psutil/issues/1101
            # https://github.com/giampaolo/psutil/issues/1129
            # https://github.com/giampaolo/psutil/issues/1245
            # https://github.com/giampaolo/psutil/issues/1323
            continue

        high = bcat(base + '_max', fallback=None)
        critical = bcat(base + '_crit', fallback=None)
        label = cat(base + '_label', fallback='').strip()

        if high is not None:
            try:
                high = float(high) / 1000.0
            except ValueError:
                high = None
        if critical is not None:
            try:
                critical = float(critical) / 1000.0
            except ValueError:
                critical = None

        ret[unit_name].append((label, current, high, critical))

    # Indication that no sensors were detected in /sys/class/hwmon/
    if not basenames:
        basenames = glob.glob('/sys/class/thermal/thermal_zone*')
        basenames = sorted(set(basenames))

        for base in basenames:
            try:
                path = os.path.join(base, 'temp')
                current = float(bcat(path)) / 1000.0
                path = os.path.join(base, 'type')
                unit_name = cat(path).strip()
            except (IOError, OSError, ValueError):
                continue

            trip_paths = glob.glob(base + '/trip_point*')
            trip_points = set(['_'.join(
                os.path.basename(p).split('_')[0:3]) for p in trip_paths])
            critical = None
            high = None
            for trip_point in trip_points:
                path = os.path.join(base, trip_point + "_type")
                trip_type = cat(path, fallback='').strip()
                if trip_type == 'critical':
                    critical = bcat(os.path.join(base, trip_point + "_temp"),
                                    fallback=None)
                elif trip_type == 'high':
                    high = bcat(os.path.join(base, trip_point + "_temp"),
                                fallback=None)

                if high is not None:
                    try:
                        high = float(high) / 1000.0
                    except ValueError:
                        high = None
                if critical is not None:
                    try:
                        critical = float(critical) / 1000.0
                    except ValueError:
                        critical = None

            ret[unit_name].append(('', current, high, critical))

    return dict(ret)
