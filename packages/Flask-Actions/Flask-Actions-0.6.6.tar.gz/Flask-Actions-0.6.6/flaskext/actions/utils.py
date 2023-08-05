#!/usr/bin/env python
# -*- encoding:utf-8 -*-
import string
import random
KEY_CHARS = string.letters + string.digits + string.punctuation

def generate_secret_key(length=32):
    return  repr(''.join(random.choice(KEY_CHARS) for _ in xrange(length)))

