# -*- coding: utf-8 *-*
import argparse


def list(sw, args):
    """
    Lists all available api calls grouped by namespace
    """
    parser = argparse.ArgumentParser(
        prog='space api list',
        description='Add child channels to an activation key add an ' +
        'activationkey for child channels.'
    )

    parser.parse_args(args)

    calls = sw.call('api.getApiCallList')

    if calls:
        for call in calls:
            for name, info in calls.items():
                for i, k in info.items():
                    print("%s.%s(%s)" % (name, k['name'], k['parameters']))
        return True
    else:
        print("No calls in api. Most likely lies")
        return False


def list_in_namespace(sw, args):
    """
    returns a dictionary of calls
    """
    parser = argparse.ArgumentParser(
        prog='space api list',
        description='List calls available in namespace'
    )
    parser.add_argument(
        '--namespace',
        default=None,
        required=True,
        help="Namespace"
    )
    parser.add_argument(
        '--test',
        default=None,
        required=False,
        help="Namespace"
    )
    p = parser.parse_args(args)

    try:
        result = sw.call(
            'api.getApiNamespaceCallList',
            p.namespace
        )
    except Exception as e:
        print("Failed to run command: %s" % e)

    print(result)
