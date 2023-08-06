#!/usr/bin/env python3
# -*- mode: python -*-
"""A pypi demonstration vehicle.

.. moduleauthor:: Andrew Carter <andrew@invalid.com>

"""

def plain_get_payload_str(msg):
    assert(is_plain(msg))
    cte = msg['Content-Transfer-Encoding']
    if cte == 'base64' or cte == 'quoted-printable':
        return str(msg.get_payload(decode = True), encoding = msg.get_content_charset())
    else: # Strange case of ascii or 8-bit messages
        return msg.get_payload(decode = False)

def uniq(array, eq = None):
    """ Uniquify sequence in way, simular to GNU uniq. """
    result = []
    if len(array) != 0:
        result.append(array[0])
        current = array[0]
        eq = eq if eq else lambda x, y: x == y
        for obj in array[1:]:
            if not eq(current, obj):
                result.append(obj)
            current = obj
    return result

def is_plain(msg):
    return msg.get_content_type() == 'text/plain'

def filter_out_html(msg):
    payload = msg.get_payload()
    if type(payload) == list:
        new_payload = list(filter(lambda obj: obj.get_content_type() != 'text/html', payload))
        msg.set_payload(new_payload)

def remove_trailing_quoting(string):
    from itertools import dropwhile
    def empty(x):
        return all(map(lambda ch: ch.isspace(), x))
    def quote(x):
        return x.startswith('>') or empty(x)
    text = reversed(string.split('\n'))
    text = list(dropwhile(quote, text))
    text.reverse()
    text = uniq(text, lambda x, y: x == y == '')
    return '\n'.join(text) + "\n"

def transform_content(plain_msg, fn):
    assert(is_plain(plain_msg))
    text = plain_get_payload_str(plain_msg)
    plain_msg.set_charset('utf-8')
    del plain_msg['Content-Transfer-Encoding']
    plain_msg.set_payload(fn(text))

def collapse_single_alternative(msg):
    payload = msg.get_payload()
    if type(payload) == list and len(payload) == 1:
        single = payload[0]
        del msg['Content-Type'], msg['Content-Transfer-Encoding']
        msg['Content-Type'] = single['Content-Type']
        msg['Content-Transfer-Encoding'] = single['Content-Transfer-Encoding']
        msg.set_payload(single.get_payload())

def reformat(msg):
    filter_out_html(msg)
    collapse_single_alternative(msg)
    if is_plain(msg):
        transform_content(msg, remove_trailing_quoting)
    else:
        for submsg in filter(is_plain, msg.get_payload()):
            transform_content(submsg, remove_trailing_quoting)
