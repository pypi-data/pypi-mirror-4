# -*- coding: utf-8 *-*
import argparse
import json
import prettytable


def list(sw, args):
    """
    List channels.

    Returns a json
    """
    parser = argparse.ArgumentParser(
        prog='space channel list',
        description='List channels in spacewalk.'
    )
    parser.add_argument(
        'type',
        choices=[
            'all',
            'user',
            'popular',
            'retired',
            'shared',
            'software',
            'vendor'
        ],
        default='popular',
        help="Type of search you would like to perform"
    )
    parser.add_argument(
        '--format',
        choices=[
            'raw',
            'json',
            'pretty'
        ],
        default='pretty',
        required=False
    )
    parser.add_argument(
        '--popcount',
        default=None,
        help=('channels with at least this many systems ' +
        'subscribed will be returned')
    )

    api_calls = {
        'all': 'channel.listAllChannels',
        'user': 'channel.listMyChannels',
        'popular': 'channel.listPopularChannels',
        'retired': 'channel.listRetiredChannels',
        'shared': 'channel.listSharedChannels',
        'software': 'channel.listSoftwareChannels',
        'vendor': 'channel.listVendorChannels'
    }

    p = parser.parse_args(args)

    if p.type == 'popular' and not p.popcount:
        print("Popular requires popcount arg.")
        parser.print_help()
        return False

    if p.popcount:
        popcount = int(p.popcount)
        results = sw.call(
            api_calls[p.type],
            popcount
        )
    else:
        results = sw.call(
            api_calls[p.type]
        )
    if results == []:
        print("Empty result set.")

    channels = []
    for result in results:
        channels.append(result)

    if p.format == 'pretty':
        """
        int "id"
        string "label"
        string "name"
        string "provider_name"
        int "packages"
        int "systems"
        string "arch_name"
        """
        if p.type == "software":
            t = prettytable.PrettyTable([
                "Label",
                "Name",
                "Parent Label",
                "End Of Life",
                "Arch"
            ])
            t.align["Label"] = "l"
            t.align["Name"] = "l"
            t.align["Parent Label"] = "l"
            t.padding_width = 1
            for c in results:

                t.add_row([
                    c['label'],
                    c['name'],
                    c['parent_label'],
                    c['end_of_life'],
                    c['arch']
                ])
        else:
            t = prettytable.PrettyTable([
                "Label",
                "Name",
                "Provider Name",
                "Packages",
                "Systems",
                "Arch Name"
            ])
            t.align["Label"] = "l"
            t.align["Name"] = "l"
            t.align["Packages"] = "r"
            t.align["Systems"] = "r"
            t.align["Provider Name"] = "l"
            t.padding_width = 1
            for c in results:

                t.add_row([
                    c['label'],
                    c['name'],
                    c['provider_name'],
                    c['packages'],
                    c['systems'],
                    c['arch_name']
                ])
        print(t)

    elif p.format == 'json':
        output = json.dumps(dict(channels=channels))
        print(output)
    else:
        for result in results:
            print(result)
    return results
