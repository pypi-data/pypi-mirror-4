"""
`main` is the main entry point for the cli
"""

import datetime
import hashlib
import json
import os
import re
import sys

import signal

from space.util import load_funcs
from space.util import get_config
from space.util import get_config_value
from space.util import get_username
from space.util import get_password
from space.util import get_hostname
from space.util import check_session_user
from space.util import print_help
from space.util import print_avail_namespace_help

import pkg_resources  # part of setuptools
version = pkg_resources.require("python-space")[0].version

if sys.version_info >= (3, 0):   # pragma: no cover
    import xmlrpc.client
    xmlrpc = xmlrpc.client

if sys.version_info <= (2, 8):   # pragma: no cover
    import xmlrpclib
    xmlrpc = xmlrpclib


# handle ctrl+c
def signal_handler(signal, frame):   # pragma: no cover
        print("")
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def main(config=None):
    """
    Main function. Entry point in which we will route any requests to modules
    or argparse.
    """

    args = sys.argv
    # remove the filename arg
    args.pop(0)

    functions = load_funcs(config)

    # pull all the switches and values
    args, flags = parse_flags(args)

    # clean up args so that cargs only contains non-switch args
    args, cargs = clean_args(args)

    try:
        flags['version']
        return version
    except KeyError:
        pass

    try:
        flags['docs']
        return print_help()
    except KeyError:
        pass

    try:
        flags['logout']
        _logout(
            config=config
        )
        return "User logged out"
    except KeyError:
        pass

    # we already pass config as an arg to this def
    # the flag will trumph all though
    if not config:
        try:
            config = os.path.expanduser(flags['config'])
        except KeyError:
            config = get_config()

    if len(cargs) == 1:
        print(
            "Usage: space [options] '<namespace>'" +
            " <command> [arguments]"
        )

        # declare variables
        namespace = None
        avail = []

        for f, inst in functions.items():
            m = re.match('([a-z]*)\.([a-z_]*)', f)
            if m.group(1) == cargs[0]:
                # set namespace variable
                namespace = m.group(1)
                avail.append(m.group(2))

        if namespace and len(avail) > 0:
            print(
                "\nAvailable commands in " +
                "\"%s\" namespace:" % namespace
            )
            for a in avail:
                print(" %s" % (a))

            print(
                "\n* For help on any individual command, " +
                "just use the --help flag after."
            )
            return False

        return print_avail_namespace_help()

    if len(cargs) < 1:
        return print_avail_namespace_help()

    # first we check version
    # then check for major flags
    # then for actual command args

    try:
        username = flags['username']
    except KeyError:
        username = get_username(config)

    # if no session is cached, then prompt
    sess_vars = check_session_user(username)

    # set password here to none
    password = None

    if not sess_vars:
        try:
            password = flags['password']
        except KeyError:
            password = get_password(config)

        try:
            hostname = flags['host']
        except KeyError:
            hostname = get_hostname(config)
    else:
        hostname = sess_vars.hostname

    # check initial arg to see if its in the modules
    if "%s.%s" % (cargs[0], cargs[1]) in functions.keys():

        # loop through loaded functions
        for f in functions.keys():
            m = re.match('([a-z]*)\.([a-z_]*)', f)
            if m:
                top = m.group(1)
                sub = m.group(2)

            # check to see if a top level command has been called
            if top in args:

                # there should be at least one more, as we dont have top level
                # commands without sub commands yet
                if sub in args:

                    # second level command is found. Start prepping that.
                    module_path = "%s.%s" % (top, sub)

                    # need to pop off the two commands we already know about
                    args.pop(0)
                    args.pop(0)

                    # if the compiled module is in our function dict, as a key,
                    # then lets feed it args and call it
                    if module_path in functions.keys():

                        sw = swSession(
                            username,
                            hostname,
                            password
                        )
                        if not sess_vars:
                            sw.login()
                        else:
                            sw.key = sess_vars.key
                        functions[module_path](sw, args)
    else:
        return print_avail_namespace_help()


def clean_args(args):
    result = []
    for arg in args:
        if not re.match('^--.*', arg):
            result.append(arg)
    return args, result


def parse_flags(args):
    """
    Parse options before commands. Once a non flag switch
    is found args are passed back with the pre switches
    split out.
    """
    result = {}
    end = False
    # this is needed because we are altering the list
    # so its necessary to return a list copy
    # http://stackoverflow.com/a/14465613/145851
    for arg in list(args):
        if end:
            return args, result

        if re.match('.*=.*', arg):
            m = re.match('^-+(.*)=(.*)', arg)
            result[m.group(1)] = m.group(2)
            index = args.index(m.group(0))
            args.pop(index)

        elif re.match('^-+(?!=).*', arg):
            m = re.match('^-+(.*)', arg)
            result[m.group(1)] = None
            index = args.index(m.group(0))
            args.pop(index)

        elif re.match('[a-zA-Z].*', arg):
            end = True
    return args, result


def _logout(
    config=None
):
    """
    Will try and handle the session logout here
    """
    login = get_username(config)
    username = login.encode('utf-8')
    ref = hashlib.md5(username).hexdigest()
    session_file = '/var/tmp/space-%s' % (ref)    

    if os.path.exists(session_file):
        os.remove(session_file)
        print("Logged out.")
    else:
        print("No active sessions.")
    return


class swSession(object):
    """
    Spacewalk Class that will be handing us a session object back.

    If the config is not present, we prompt for values needed
    to authenticate our Spacewalk session.
    """

    def __init__(
        self,
        username,
        hostname=None,
        password=None,
        sess_key=None,
        timeout=300
    ):
        """
        returns swsession
        """
        self.hostname = hostname
        self.username = username
        self.__password = password
        self.timeout = timeout
        self.key = sess_key
        self.server_api = "https://%s/rpc/api" % self.hostname
        self.server_push = "https://%s/APP" % self.hostname

        self.session = xmlrpc.Server(self.server_api, verbose=0)

    def check_session(self):
        now = int(datetime.datetime.now().strftime('%s'))
        username = self.username.encode('utf-8')
        ref = hashlib.md5(username).hexdigest()
        session_file = '/var/tmp/space-%s' % (ref)

        # load session data if file exists
        if os.path.exists(session_file):
            created = os.path.getctime(session_file)

            if (now - created) > self.timeout:
                return False
            else:
                f = open(session_file, 'r')
                self.key = f.readlines()[0]
                return True
        return False

    def save_session(self):
        username = self.username.encode('utf-8')
        ref = hashlib.md5(username).hexdigest()
        session_file = '/var/tmp/space-%s' % (ref)
        try:
            with open(session_file, 'w+') as f:
                f.write("%s %s %s" % (self.key, self.hostname, self.timeout))

        except OSError as e:
            print("Could not save session file: %s" % e)
            sys.exit(1)

    def login(self):
        if self.check_session() is False:
            try:
                # actually login
                self.key = self.session.auth.login(
                    self.username,
                    self.__password,
                    self.timeout
                )
                self.save_session()
            except Exception as e:
                sys.exit("Login to %s Failed. %s" % (self.server_api, e))

        return self.key

    def call(self, ns, *args):
        """
        note: args must be a list that we can unpack,
        even if there is 0 args, it needs to unpack
        """

        func = getattr(self.session, ns)

        try:
            return func(self.key, *args)
        except Exception as e:
            print("Action failed: %s" % e.faultString)
            return False
