# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2011-10-21
#  Copyright (c) 2011 Martin J. Laubach. All rights reserved.
#
# ------------------------------------------------------------------------

"""
This package provides simple access to the austrian RTR (Rundfunk und Telekom
Regulierungs-GmbH) "ECG list", the registry of persons and companies who do
not wish to receive promotional e-mail.

Typical usage looks like this::

    from ecglist import ECGList

    e = ECGList()
    if email not in e:
        send_email(email)
    else:
        print "%s does not want to receive email" % email
"""

__version__ = '1.1'

import hashlib

# ------------------------------------------------------------------------
class ECGList(object):
    """
    I am a simple wrapper class for accessing the austrian RTR GmbH
    do-not-email blacklist.
    """

    NOT_EMAIL_ADDRESS   = 1
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
        """
        External use deprecated, use get_blacklist_status(..., numeric=True)
        """
        if '@' in email:
            email = email.lower()
            name, domain = email.split('@', 1)

            if hashlib.sha1("@" + domain).digest() in self.hash_values:
                return self.DOMAIN_BLACKLISTED
            if hashlib.sha1(email).digest() in self.hash_values:
                return self.ADDRESS_BLACKLISTED
            return None

        return self.NOT_EMAIL_ADDRESS

    def get_blacklist_status(self, email, numeric=False):
        """
        Search an email address in the blacklist. Returns either
        None or a status. The status is either a string describing
        the type of listing or a numeric status code (if numeric=True)
        """
        status = self.get_blacklist_status_code(email)
        if numeric:
            return status
        return self.status_str[status] if status else None

    def __contains__(self, email):
        """
        Implement "in" operator. Return True if email is blacklisted,
        False otherwise
        """
        return self.get_blacklist_status_code(email)

    def __getitem__(self, email):
        """
        Implement indexing operator. Return result as of get_blacklist_status()
        """
        return self.get_blacklist_status_code(email)

# ------------------------------------------------------------------------
