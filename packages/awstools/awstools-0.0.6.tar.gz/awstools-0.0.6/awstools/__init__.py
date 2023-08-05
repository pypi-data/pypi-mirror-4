import os
from ConfigParser import ConfigParser

import boto


_defaults = {}


def read_config(alternate_config=None):
    """Helper for the configuration"""
    _config = ConfigParser(_defaults)
    if alternate_config:
        _config.read(os.path.expanduser(alternate_config))
    else:
        _config.read(['awstools.cfg',
                      os.path.expanduser('~/.awstools.cfg'),
                      '/etc/awstools.cfg'])
    return _config


def find_stacks(pattern=None, findall=False):
    """Return a list of stacks matching a pattern"""

    cfn = boto.connect_cloudformation()
    stacks = []
    next_token = None
    while True:
        rs = cfn.list_stacks(next_token=next_token)
        stacks.extend(rs)
        next_token = rs.next_token
        if next_token is None:
            break

    if pattern:
        stacks = [s for s in stacks if pattern in s.stack_name]

    if not findall:
        INVALID_STATUS = ["DELETE_COMPLETE"]
        stacks = [s for s in stacks if s.stack_status not in INVALID_STATUS]

    return sorted(stacks, key=lambda k: k.stack_name)


def find_one_stack(pattern, findall=False, summary=True):
    """Return the result is there is only one. Raise ValueError otherwise"""
    stacks = find_stacks(pattern=pattern, findall=findall)

    for stack in stacks:        # If we have an exact match, just take it
        if stack.stack_name == pattern:
            stacks = [stack]
            break

    if len(stacks) > 1:
        raise ValueError("More than one stack matched this pattern: %s" % pattern)
    if len(stacks) == 0:
        raise ValueError("No stack found with pattern: %s" % pattern)
    if summary:
        return stacks[0]
    else:
        cfn = boto.connect_cloudformation()
        return cfn.describe_stacks(stacks[0].stack_name)[0]
