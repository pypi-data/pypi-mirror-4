# -*- coding: utf-8 *-*
import argparse
import sys


def add_child_channels(sw, args):
    """
    Add child channels to an activation key
    """
    parser = argparse.ArgumentParser(
        prog='space activationkey add_child_channels',
        description='Add child channels to an activation key.'
    )

    parser.add_argument(
        '--keyname', '-k',
        default=None,
        required=True,
        help="Name of the activationkey"
    )
    parser.add_argument(
        '--channels', '-c',
        default=None,
        required=True,
        nargs='+',
        type=str,
        help="Channels listed in space delimitted list."
    )
    p = parser.parse_args(args)

    result = sw.call(
        'activationkey.addChildChannels',
        p.keyname,
        p.channels
    )
    print("%s added to %s" % (p.channels, p.keyname))
    return True


def create(sw, args):
    """
    Create new activation key

    """
    parser = argparse.ArgumentParser(
        prog='space activationkey create',
        description='Create a new activation key with unlimited usage.' +
        ' The activation key parameter passed in will be prefixed ' +
        'with the organization ID, and this value will be returned from ' +
        'the create call. Eg. If the caller passes in the key "foo" and ' +
        'belong to an organization with the ID 100, the actual activation ' +
        'key will be "100-foo"'
    )
    parser.add_argument(
        '-k', '--keyname',
        default=None,
        required=True,
        help="Name of the activationkey"
    )
    parser.add_argument(
        '-b',
        '--basechannel',
        default=None,
        required=True,
        help="baseChannelLabel, "
    )
    parser.add_argument(
        '--monitoring_entitled',
        action='store_true',
        help="monitoring_entitled?"
    )
    parser.add_argument(
        '--provisioning_entitled',
        action='store_true',
        help="provisioning_entitled?"
    )
    parser.add_argument(
        '--virtualization_host',
        action='store_true',
        help="virtualization_host?"
    )
    parser.add_argument(
        '--virtualization_host_platform',
        action='store_true',
        help="virtualization_host_platform?"
    )
    parser.add_argument(
        '--universal_default',
        action='store_true',
        help="universal_default?"
    )    
    p = parser.parse_args(args)

    entitlements = []
    if p.monitoring_entitled:
        entitlements.append('monitoring_entitled')

    if p.provisioning_entitled:
        entitlements.append('provisioning_entitled')

    if p.virtualization_host:
        entitlements.append('virtualization_host')

    if p.virtualization_host_platform:
        entitlements.append('virtualization_host_platform')

    try:
        result = sw.call(
            'activationkey.create',
            p.keyname,
            p.keyname,
            p.basechannel,
            entitlements,
            p.universal_default
        )
    except Exception as e:
        print("Error adding key: %s" % e.faultString)

    if result:
        print("%s created" % result[0])
    return result


def add_group(sw, args):
    """
    Provided a group and a activationkey adds the group to the activationkey
    """
    parser = argparse.ArgumentParser(
        prog='space activationkey add_group',
        description='Provided a group and a activationkey ' +
        'adds the group to the activationkey'
    )
    parser.add_argument(
        '-k',
        '--keyname',
        default=None,
        required=True,
        help="Name of the activationkey"
    )
    parser.add_argument(
        '-g',
        '--groups',
        default=None,
        required=True,
        nargs='+',
        type=str,
        help='Space delimitted list of system groups'
    )
    p = parser.parse_args(args)

    groups_ids = []
    result = None
    for group in p.groups:
        try:
            groupid = sw.call(
                'systemgroup.getDetails',
                group
            )
            gid = groupid['id']
            groups_ids.append(int(gid))

        except Exception as e:
            print("Failed: %s" % e)

    try:
        result = sw.call(
            'activationkey.addServerGroups',
            p.keyname,
            groups_ids
        )
    except Exception as e:
        print ("Adding key to group failed: %s" % e)

    if result == 1:
        for group in p.groups:
            print("%s has been added to %s" % (group, p.keyname))
    else:
        print(result)

    return result

