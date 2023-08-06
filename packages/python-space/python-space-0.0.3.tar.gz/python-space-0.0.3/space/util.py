import datetime
import hashlib
import imp
import os
import sys

from collections import namedtuple
from getpass import getpass

if sys.version_info >= (3, 0):  # pragma: no cover
    import xmlrpc.client
    xmlrpc = xmlrpc.client
    from configparser import ConfigParser
    from configparser import NoOptionError

if sys.version_info <= (2, 8):  # pragma: no cover
    import xmlrpclib
    xmlrpc = xmlrpclib
    from ConfigParser import ConfigParser
    from ConfigParser import NoOptionError


def check_session_user(
    username,
    session_file=None
):
    now = int(datetime.datetime.now().strftime('%s'))
    ref = hashlib.md5(username.encode('utf-8')).hexdigest()
    if session_file is None:
        session_file = '/var/tmp/space-%s' % (ref)

    # load session data if file exists for user else create
    if os.path.exists(session_file):
        created = os.path.getctime(session_file)

        f = open(session_file, 'r')

        session_vars = f.readlines()[0].split(' ')

        if (now - created) > int(session_vars[2]):
            os.remove(session_file)
            return False
        else:
            n = namedtuple('Session', 'key, hostname')
            return n(session_vars[0], session_vars[1])
    return False


def load_funcs(config=None):

    modules = list()
    modules_dict = dict()
    functions = dict()
    module_dir = None

    module_dir = get_config_value(config, 'module_dir')
    if module_dir is None:
        module_dir = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'modules'
        )

    # loop through files in the module dir
    for mod_ in os.listdir(module_dir):
        if mod_.startswith('_'):
            continue
        bare_ = mod_.rfind('.')
        if bare_ > 0:
            naked_ = mod_[:bare_]
        modules_dict[naked_] = mod_

    # loop through dict and load modules. Using the imp module here
    # to programatically load these modules
    for m, k in modules_dict.items():
        mod_, path, desc = imp.find_module(m, [module_dir])
        module = imp.load_module(m, mod_, path, desc)
        modules.append(module)

    # ripping out the name and functions of each module
    for mod in modules:
        module_name = mod.__name__.rsplit('.', 1)[-1]
        # listing attributes to find actual functions
        for attr in dir(mod):
            attr_name = '{0}.{1}'.format(module_name, attr)
            if attr.startswith('_'):
                continue
            if callable(getattr(mod, attr)):
                func = getattr(mod, attr)
                # Ignore exception functions
                if any(['Error' in func.__name__,
                        'Exception' in func.__name__]):
                    continue
                # add callable function to our loaded lib
                functions[attr_name] = func

    # Loop through and inject some sweetness into here.
    for mod in modules:
        if not hasattr(mod, '__sweet__'):
            mod.__sweet__ = functions

    return functions


def _check_length(subject):
    if len(subject.strip()) == 0:
        raise ValueError("Value has length of 0")


def get_config():
    """
    Check for a config in all the usual places, should you 
    not find it, return None
    """
    places = [
        "{0}/.space/config.ini".format(os.path.expanduser('~')),
        "/etc/space/config.ini"
    ]

    for place in places:
        if os.path.exists(place):
            return place
    return None


def get_config_value(config, key):
    confparse = ConfigParser()
    try:
        confparse.read(config)
        value = confparse.get('space', '%s' % key)
        _check_length(value)
    except Exception:
        return None

    return value


def get_password(
    config=None,
    getpass=getpass
):
    """
    prompts for a password for an existing user
    """

    if config is None:
        config = get_config()

    password = get_config_value(config, 'password')

    # we only need the getpass stuff if prompting for passwords.
    # This only happens on session init.
    if password is None:
        password = getpass(
            'Please enter the spacewalk password: '
        )
    return password.strip()


def get_username(
    config=None
):
    """
    This will get a username, whether from a config,
    or if nothing exists in the config, from getpass.getuser
    """
    if config is None:
        config = get_config()
    # hack to deal with py2/py3
    try:  # pragma: no cover
        inputs = raw_input
    except:  # pragma: no cover
        inputs = input

    username = get_config_value(config, 'username')
    if username is None:
        username = str(
            inputs('Please enter your spacewalk username: ')
        ).strip()
    return username


def get_hostname(
    config=None
):
    """
    asks user for username.
    """
    if not config:
        config = get_config()
    # hack to deal with py2/py3
    try:  # pragma: no cover
        inputs = raw_input
    except:  # pragma: no cover
        inputs = input

    hostname = get_config_value(config, 'hostname')
    if hostname is None:
        hostname = str(inputs('Please enter a spacewalk host: ')).strip()
    return hostname


def print_help():
    functions = load_funcs()
    print("Help Docs\n")
    for func, inst in functions.items():
        print("space %s %s" % (
            func.split(".")[0], func.split(".")[1])
        )
        print(inst.__doc__)
    return functions


def print_short_help():
    functions = load_funcs()
    print(
        "Usage: space [options] '<namespace>' <command> [arguments]" +
        "\nFor detailed help on " +
        "any one command: [command] --help \n" +
        "\nAvailable Commands\n" +
        "------------------"
    )
    for func, inst in functions.items():
        print("space %s %s" % (
              func.split(".")[0], func.split(".")[1])
              )
    return functions


def print_avail_namespace_help():
    functions = load_funcs()
    print(
        "Usage: space [options] '<namespace>' <command> [arguments]\n" +
        "Options:\n" +
        "    --username         Spacewalk login name\n" +
        "    --password     Spacewalk password\n" +
        "    --host         Spacewalk host\n" +
        "    --config       optional config file to pass user/pass/host\n" +
        "                   info\n" +
        "    --docs         Print full docs to the terminal\n"
        "\nFor detailed help on \n" +
        "any one command: [command] --help \n" +
        "\nAvailable Namespaces\n" +
        "------------------"
    )
    funcs = []
    for func, inst in functions.items():
        f = func.split(".")[0]
        if f not in funcs:
            funcs.append(f)

    for top in funcs:
        print(" %s" % (top))
