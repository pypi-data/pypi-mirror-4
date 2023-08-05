# -*- coding: utf-8 -*-

def lower_keys(headers):
    """
    Lowercases all keys in the given dictionary to remove inconsistencies
    between "Content-Type" and "Content-type". This is particularly useful for
    comparing two sets of headers that may or may not retain the same case
    formatting.
    """
    new_headers = {}
    for key in headers.keys():
        new_headers[key.lower()] = headers[key]
    return new_headers
