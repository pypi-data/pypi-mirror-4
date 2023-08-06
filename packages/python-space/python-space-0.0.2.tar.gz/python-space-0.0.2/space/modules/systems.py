# -*- coding: utf-8 *-*
import argparse


def child_channels(
    sw,
    args
):
    """
    List child channels for system
    """
    parser = argparse.ArgumentParser(
        prog='space systems child_channels',
        description=(
            'This command lists child' +
            'channels assigned to a server'
        )
    )
    parser.add_argument(
        '--sid',
        default=None,
        required=False,
        help="Server ID number"
    )
    parser.add_argument(
        '--server',
        default=None,
        required=False,
        help="Servername"
    )

    p = parser.parse_args(args)

    if p.sid:
        channels = sw.call(
            'system.listSubscribedChildChannels',
            int(p.sid)
        )

    elif p.server:
        try:
            server = _get_system(sw, p.server)
            if server == []:
                print("No servers were found.")
                return False
            
            channels = _get_channels(sw, server[0]['id'])

        except Exception as e:
            print("Exception: %s" % e)
            return False

    else:
        parser.print_help()
        return False

    for channel in channels:
        print(channel['name'])

    return True


# helper functions
def _get_system(sw, server):
    res = sw.call(
        'system.getId',
        [server]
    )
    return res


def _get_channels(sw, serverid):
    channels = sw.call(
        'system.listSubscribedChildChannels',
        [serverid]
    )
    return channels


def list(sw, args):
    """
    List Systems in spacewalk, either by group or
    just all of em.
    """

    parser = argparse.ArgumentParser(
        prog='space systems listsystems',
        epilog='For detailed help ' +
        'pass --help to a target',
        description=('This command will ' +
        'list all spacewalk systems.')
    )
    parser.add_argument(
        '-g', '--group',
        default=None,
        required=False,
        help="System Group Name"
    )

    p = parser.parse_args(args)

    _systems = None

    if p.group:
        try:
            _systems = sw.call(
                'systemgroup.listSystems',
                p.group
            )
        except Exception as e:
            print("Error listing systems: %s" % e)
            return False

        if _systems:
            for s in _systems:
                print("%s %s" % (s['hostname'], s['id']))
            return _systems
        else:
            print("No servers in group")
            return False
    else:
        try:
            _systems = sw.call(
                'system.listSystems'
            )
        except Exception as e:
            print("Error listing all systems: %s" % e)
            return False
        if _systems:
            for s in _systems:
                print("%s %s" % (s['name'], s['id']))
            return _systems
        else:
            print("No servers in group")
            return False
