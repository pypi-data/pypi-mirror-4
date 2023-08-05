from poodledo.apiclient import ApiClient,PoodledoError,ToodledoError
from getpass import getpass
from os import mkdir
from os.path import exists, expanduser, join
from sys import exit

try:
    from ConfigParser import SafeConfigParser,NoOptionError,NoSectionError
except ImportError: 
    from configparser import SafeConfigParser,NoOptionError,NoSectionError

CONFIGDIR  = expanduser("~/.tdcli")
CONFIGFILE = join(CONFIGDIR, "tdclirc")

def get_config():
    config = SafeConfigParser()
    config.read(CONFIGFILE)
    return config

def store_config(config):
    if not exists(CONFIGDIR):
        mkdir(CONFIGDIR)
    cfile = open(CONFIGFILE, 'w')
    config.write(cfile)
    cfile.close()

def read_or_get_creds(config):
    username = ""
    password = ""

    try:
        username = config.get('config', 'username')
        print("Username:", username)
    except (NoOptionError, NoSectionError):
        print("Please enter your login credentials.")
        username = raw_input("Username: ")

    try:
        password = config.get('config', 'password')
    except (NoOptionError, NoSectionError):
        password = getpass("Password: ")

    return (username, password)

def get_tag(config):
    tag = None
    try:
        tag = config.get('filter', 'tag')
    except (NoSectionError, NoOptionError):
        pass
    return tag

def get_cutoff(config):
    cutoff = None
    try:
        cutoff = int(config.get('filter', 'priority'))
    except (NoSectionError, NoOptionError):
        cutoff = -1
    return cutoff

def do_login(config=None):
    client = ApiClient()
    if not config:
        config = get_config()
    try:
        client.application_id = config.get('application', 'id')
        client.application_token = config.get('application', 'token')

    except (NoSectionError, NoOptionError):
        raise PoodledoError("Application ID or token not specified in %s.\nGenerate such at 'https://api.toodledo.com/2/account/doc_register.php?si=1'. Dying." % CONFIGFILE)

    try:
        client._key = config.get('session', 'key')
        client.getAccountInfo()

    except (NoSectionError, NoOptionError, ToodledoError):
        # cached session key either wasn't there or wasn't good; get a new one and cache it
        client._key = None
        (username, password) = read_or_get_creds(config)

        try:
            client.authenticate(username, password)
        except ToodledoError as e:
            print("No login credentials were successful; please try again.")
            raise e

        if not config.has_section('session'):
            config.add_section('session')
        config.set('session', 'key', client.key)
        store_config(config)

    return client
