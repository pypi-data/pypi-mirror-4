# -*- coding: utf-8 *-*
import argparse
import re
import sys
import subprocess

from space.util import get_username
from space.util import get_password

if sys.version_info >= (3, 0):  # pragma: no cover
    import urllib.request as urllib
if sys.version_info <= (2, 8):  # pragma: no cover
    import urllib


def getpackage(sw, args):
    """
    Download a package to the current directory

        -p, --pid       define a package id.

    """
    parser = argparse.ArgumentParser(
        prog='space packages getpackage',
        description='Download a package.'
    )
    parser.add_argument(
        '-p',
        '--pid',
        default=None,
        required=True,
        help="Package ID"
    )

    arg = parser.parse_args(args)

    pkg_url = sw.call(
        'packages.getPackageUrl',
        int(arg.pid)
    )

    pkg = re.match(".*/(.*.rpm$)", pkg_url)
    result = urllib.urlretrieve(pkg_url, pkg.group(1))

    print("Downloaded %s" % result[0])
    return


def copy(sw, args):
    """
    Copy a package into a channel.

        -p, --pid       define a package id.
        -c, --channel   define spacewalk channel
    """
    parser = argparse.ArgumentParser(
        prog='space packages copy',
        description='Copy a package into a channel by id.'
    )
    parser.add_argument(
        '-p',
        '--pid',
        default=None,
        required=True,
        help="Package ID"
    )
    parser.add_argument(
        '-c',
        '--channel',
        default=None,
        required=True,
        help="Channel ID"
    )

    arg = parser.parse_args(args)

    result = sw.call(
        'channel.software.addPackages',
        arg.channel,
        [int(arg.pid)]
            
    )
    print("Result: %s" % result)