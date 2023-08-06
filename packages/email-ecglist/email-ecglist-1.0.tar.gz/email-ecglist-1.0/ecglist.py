# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2011-10-21
#  Copyright (c) 2011 Martin J. Laubach. All rights reserved.
#
# ------------------------------------------------------------------------

__version__ = '1.0'

import hashlib

# ------------------------------------------------------------------------
class ECGList(object):
    NOT_EMAIL_ADDRESS    = 1
    DOMAIN_BLACKLISTED  = 2
    ADDRESS_BLACKLISTED = 3

    status_str = {
        NOT_EMAIL_ADDRESS:   "Not an email address",
        DOMAIN_BLACKLISTED:  "Domain blacklisted",
        ADDRESS_BLACKLISTED: "Address blacklisted"
    }

    def __init__(self, filename="ecg-liste.hash"):
        hash_values = {}
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(20)
                if len(chunk) < 20:
                    break
                hash_values[chunk] = 1

        self.hash_values = hash_values

    def get_blacklist_status_code(self, email):
        if '@' in email:
            email = email.lower()
            name, domain = email.split('@', 1)

            if hashlib.sha1("@" + domain).digest() in self.hash_values:
                return self.DOMAIN_BLACKLISTED
            if hashlib.sha1(email).digest() in self.hash_values:
                return self.ADDRESS_BLACKLISTED
            return None

        return self.NOT_EMAIL_ADDRESS

    def get_blacklist_status(self, email):
        status = self.get_blacklist_status_code(email)
        return self.status_str[status] if status else None

# ------------------------------------------------------------------------
