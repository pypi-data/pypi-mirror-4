# fbf/utils/id.py
#
#

""" id related functions. """

## fbf imports

from fbf.utils.generic import toenc

## basic imports

import uuid

## getrssid function

def getrssid(url, time):
    """ get an id based on url and time. """
    key = str(url) + str(time)
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, toenc(key)))
