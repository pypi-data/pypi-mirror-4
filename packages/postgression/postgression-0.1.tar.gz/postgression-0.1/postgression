#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""postgression - A python client for the postgression API."""


from requests import get


def provision():
    """Provision a new database using the postgression API.

    :rtype: str
    :returns: A PostgreSQL database URL.
    """
    return get('http://api.postgression.com').text


if __name__ == '__main__':
    try:
        print provision()
    except:
        print 'ERROR! A database cannot be provisioned at this time.'
