#!/usr/bin/python

import re
import sys
import time
import urllib.request as req
import xml.etree.ElementTree as ET

from collections import defaultdict, deque
from datetime import datetime
from functools import partial
from platform import uname
from subprocess import check_output


__author__ = 'Thorsten Weimann'
__version__ = '0.3'
__license__ = 'MIT'

SLEEP_SECS = 5.0
DEFAULT_FORMAT = (
    'CPU: {model}@{speed:<5} '
    'ESSID: {essid} [{quality}] '
    '{system} {release} {machine} '
    'Gmail: {gmail_count:<3} {date} {time}'
)
GMAIL_REALM = 'New mail feed'
GMAIL_URI = 'https://mail.google.com/mail/feed/atom'
ENC = sys.getfilesystemencoding()
SYSINFO = uname()._asdict()

# re's
net = {
    'essid': re.compile(r'ESSID:"(?P<essid>.+)"', re.I),
    'tx': re.compile(r'Tx\-Power=(?P<tx>\d+)', re.I),
    'quality': re.compile(r'Link Quality=(?P<quality>\d+/\d+)', re.I),
    'rate': re.compile(r'Bit Rate=(?P<rate>\d+ [a-zA-Z]+)', re.I),
    'level': re.compile(r'Signal Level=(?P<level>[+-]\d+ [a-zA-Z]+)', re.I),
}

cpu = {
    'vendor': re.compile(r'vendor_id\s+:\s+(?P<vendor>.+)', re.I),
    'model': re.compile(r'model name\s+:\s+(?P<model>.+)', re.I),
    'speed': re.compile(r'cpu MHz\s+: (?P<speed>\d+)', re.I),
}

actions = deque()


def get_wireless_info(interface='wlan0', encoding=None, additional=None):
    """Reads basic info about your wireless interface using iwconfig.

    :parameters:
        interface : str
            WLAN interface (default: wlan0).
        encoding : str
            Your filesystemencoding, to decode the iwconfig output
            (default: None). Filesystemencoding is attached automatically.
        additional : dict
            An optional dict mapping names to regular expressions.

    The following keys are returned:

    :essid: Your ESSID
    :tx: TX-Power
    :quality: Link quality
    :rate: Bit Rate per second
    :level: Signal level

    And any additional information you pass in.
    """
    d = {}
    info = additional or {}
    info.update(net)
    out = check_output(['iwconfig', interface])
    out = out.decode(encoding or ENC)
    for name, regex in info.items():
        match = regex.search(out)
        d[name] = match.group(name)
    return d


def get_cpu_info(additional=None):
    """Reads some basic info from /proc/cpuinfo.

    :parameters:
        additional : dict
            An optional dict mapping names to regular expressions.

    The following keys are returned:

    :vendor: Vendor ID
    :model: Model name
    :speed: Speed in MHz

    And any additional information you pass in.
    """
    d = {}
    info = additional or {}
    info.update(cpu)
    with open('/proc/cpuinfo') as fp:
        data = fp.read()
    for name, regex in info.items():
        match = regex.search(data)
        d[name] = match.group(name)
    return d


def get_gmail_count(user, passwd):
    """Counts new mails for your Gmail account. This is done by parsing
    the provided newsfeed. Your mailbox (IMAP, POP) gets not connected
    every time.

    :parameters:
        user : str
            Gmail username (email address).
        passwd : str
            Password for your Gmail account.

    Returned is only one key:

    :gmail_count: Number of new (unread) messages.
    """
    gmail = dict(realm=GMAIL_REALM, uri=GMAIL_URI, user=user, passwd=passwd)
    auth_handler = req.HTTPBasicAuthHandler()
    auth_handler.add_password(**gmail)
    opener = req.build_opener(auth_handler)
    with opener.open(gmail['uri']) as response:
        root = ET.fromstring(response.read())
    count = root.find('{http://purl.org/atom/ns#}fullcount').text
    return dict(gmail_count=count)


def get_date_time(date_format='%Y-%m-%d', time_format='%H:%M'):
    """Returns actual date and time. You can use this or the builtin function
    provided by spectrwm.

    :parameters:
        date_format : str
            Format string for the date. See Python docs for usable formats
            (default: '%Y-%m-%d').
        time_format : str
            See date_format (default: '%H:%M').

    Returned are two keys:

    :date: Date formatted with date_format
    :time: Time formatted with time_format
    """
    dt = datetime.now()
    return dict(date=dt.strftime(date_format), time=dt.strftime(time_format))


def info_collector(*args, **kwargs):
    def wrapped(f):
        actions.append(partial(f, *args, **kwargs))
        return f
    return wrapped


def register(func, *args, **kwargs):
    actions.append(partial(func, *args, **kwargs))


def register_builtins():
    actions.extend([
        get_cpu_info,
        get_wireless_info,
        get_date_time,
    ])


def loop(format_str=DEFAULT_FORMAT, sleep_secs=SLEEP_SECS):
    """Main loop. Loops every `sleep_secs` over the registered functions
    and returns the collected information formatted with `format_str`.

    :parameters:
        format_str : str
            String which will be outputted on every loop.
        sleep_secs : float
            Time to sleep after every loop.

    Some static keys are present in the context (from uname output)::

        system, node, release, version, machine, processor

    Note that some values from uname can be empty. See Python docs
    (platform.uname) for details.

    Kill the loop with CTRL+C (when testing).
    """
    d = defaultdict(lambda: '-', SYSINFO)
    try:
        while True:
            for func in actions:
                try:
                    ret = func()
                    d.update(ret)
                except Exception as e:
                    sys.stderr.write(str(e) + '\n')
            sys.stdout.write(format_str.format_map(d) + '\n')
            sys.stdout.flush()
            time.sleep(sleep_secs)
    except KeyboardInterrupt:
        sys.stderr.write('\rShutting down specbar...\n')


if __name__ == '__main__':
    register_builtins()
    loop()

