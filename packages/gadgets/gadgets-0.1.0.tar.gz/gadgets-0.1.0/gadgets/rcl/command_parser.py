# -*- coding: utf-8 -*-
import re
import json



number_re = re.compile('[0-9-]*\.?[0-9]+')
command_re = re.compile('(?:^|(?<=\s))[0-9]*\.?[0-9]+(?=\s|$)')
    
def split_command(command, match):
    start = match.start()
    end = match.end()
    event, value, units = command[:start].strip(), command[start:end], command[end:].strip()
    if event.endswith(' for'):
        event = event[:-4]
    elif event.endswith(' to'):
        event = event[:-3]
    return event, float(value), units

def parse_command(command, message=None):
    command = command.strip()
    match = number_re.search(command)
    if match:
        event, value, units = split_command(command, match)
        message = {'value': value, 'units': units}
    else:
        event = command
        message = message
    return str(event), message
