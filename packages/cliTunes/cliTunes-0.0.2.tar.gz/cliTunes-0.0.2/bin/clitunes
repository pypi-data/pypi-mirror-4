#!/usr/bin/env python

from __future__ import print_function

import sys, os
import subprocess, shlex

# Ability to provide preference in environment for default command
try:
    default_command = os.environ['ITUNESPY_DEFAULT_COMMAND']
except KeyError:
    default_command = 'playpause'

# Mapping of custom commands
commands = {
    'next': 'to next track',
    'skip': 'to next track',

    'previous': 'to previous track',
    'prev': 'to previous track',

    'ff': 'to fast forward',
    'rw': 'to rewind'
}

# Base command for sending signals to iTunes
base_command = "osascript -e 'tell application \"iTunes\" {0}'"

unknown_command_error = 'The variable {0} is not defined.'
unknown_error = "An unexpected iTunes error occured. Details are as follows:\n{0}"

if len(sys.argv) > 1:
    command_name = ' '.join(sys.argv[1:]).lower()
else:
    command_name = default_command

if command_name in commands:
    command_name = commands[command_name]
else:
    command_name = 'to {0}'.format(command_name)

command = base_command.format(command_name)

process = subprocess.Popen(shlex.split(command),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

return_code = process.wait()

if return_code != 0:
    error = process.stderr.read()
    unknown_command = unknown_command_error.format(command_name)

    if unknown_command in error:
        print('{0} is an unsupported command.'.format(command_name), file=sys.stderr)
    else:
        print(unknown_error.format(error), file=sys.stderr)

sys.exit(return_code)

