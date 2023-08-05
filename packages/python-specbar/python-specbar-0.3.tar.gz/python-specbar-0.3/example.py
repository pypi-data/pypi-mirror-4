#!/usr/bin/env python

import os
import random

import specbar


def monitor_dir(directory, name):
    """Stupid function that counts files in a given directory."""
    filecount = len([x for x in os.listdir(directory) if os.path.isfile(x)])
    return {name: filecount}


# Register CPU information (builtin)
specbar.register(specbar.get_cpu_info)

# Register own function for two directories
specbar.register(monitor_dir, '/home/user/important_dir', 'imp1')
specbar.register(monitor_dir, '/home/user/very_important_dir', 'imp2')

# Register own function using decorator syntax
@specbar.info_collector()
def fortune_number():
    return dict(fortune_number=random.randint(1, 100))

# Build format string
myformat = (
    'CPU: {model}@{speed:<5} IMP: {imp1:<3} VIMP: {imp2:<3} '
    'Fortune number: {fortune_number}'
)

# Call main loop
specbar.loop(myformat)
