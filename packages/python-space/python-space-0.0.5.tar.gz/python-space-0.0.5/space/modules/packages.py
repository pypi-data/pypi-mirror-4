# -*- coding: utf-8 *-*
import argparse
import re
import sys
import subprocess

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
        required=False,
        help="Package ID"
    )
    parser.add_argument(
        '-c',
        '--channel',
        default=None,
        required=True,
        help="Channel ID"
    )

    parser.add_argument(
        '--nvr',
        default=None,
        required=False,
        help="Full Name-Version-Relase of package"
    )

    arg = parser.parse_args(args)

    if arg.pid and not arg.nvr:
        result = _add_packages_to_channel(
            sw,
            arg.channel,
            int(arg.pid)
        )

        if result:
            print(
                ("Copied package id: [ {0} ] " +
                 " INTO [ {0} ] successfully!").format(arg.channel)
            )
            return result

    # Handle the search and move if nvr
    elif arg.nvr and not arg.pid:

        # return tuple for lucene search
        pkg = _parse_nvr(arg.nvr)

        if not pkg:
            return False

        # perform search, will return false if empty result
        pkg_search = _search_package_advanced(sw, pkg)

        if pkg_search:
            # add package to channel
            result = _add_packages_to_channel(
                sw,
                arg.channel,
                pkg_search[0]['id']
            )

            if result == 1:
                print((
                    "Copied package: [ {0} ] ( {1} ) " +
                    "INTO [ {2} ] successfully!").format(
                        pkg_search[0]['id'], arg.nvr, arg.channel
                    )
                )
                return True

    else:
        print("Need to pass either Package ID or NVR.")
        return False

    return False


def _parse_nvr(nvr):
    match_obj = re.search(
        '^([a-zA-Z0-9-_]*)-([0-9.]*)-([a-zA-Z0-9-_:.]*)',
        nvr
    )
    try:
        return (match_obj.group(1), match_obj.group(2), match_obj.group(3))
    except AttributeError:
        print("Could not parse Name-Version-Relase")
        return False


def _search_package_advanced(sw, nvr_list):
    try:
        pkg_search = sw.call(
            'packages.search.advanced',
            "name:\"%s\" AND version:\"%s\" AND release:\"%s\"" % (
                nvr_list[0], nvr_list[1], nvr_list[2])
        )
        if pkg_search == []:
            print("Returned empty list.")
            return False
    except TypeError as e:
        print("Exception caught: %s" % e)
        return False

    return pkg_search


def _add_packages_to_channel(sw, channel, pkg):
    result = sw.call(
        'channel.software.addPackages',
        channel,
        [pkg]
    )
    return True
