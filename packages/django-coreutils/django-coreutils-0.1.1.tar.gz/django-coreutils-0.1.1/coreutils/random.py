# coding: utf8

import os


SEQUENCE_VALUES = (
    '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
)


def generate_salt(length=16):
    return ''.join(map(
        lambda x: SEQUENCE_VALUES[ord(x) % len(SEQUENCE_VALUES)],
        os.urandom(length)
    ))
