========
ECG List
========

This package provides simple access to the austrian RTR (Rundfunk und Telekom
Regulierungs-GmbH) "ECG list", the registry of persons and companies who do
not wish to receive promotional e-mail.

Typical usage looks like this::

    from ecglist import ECGList

    e = ECGList()
    if not e.get_blacklist_status_code(email):
        send_email(email)
    else:
        print "%s does not want to receive email" % email


Usage
-----

Set up the interface::

    from ecglist import ECGList

    # Defaults to reading "ecg-liste.hash" in current directory
    blacklist = ECGList(filename="my-ecg-list.hash")

Test for an email address being in the blacklist::

    "foo@bar.example" in blacklist

Get an email's status code::

    code = blacklist["foo@bar.example"]

`code` will be None if the email address was not found in the blacklist or
a status code indicating the type of match otherwise.

Same, but get a human readable string instead of a status code::

    status_str = blacklist.get_blacklist_status("foo@bar.example")


Background
----------

Service providers that send unsolicited advertising e-mail have to observe this list.
Please refer to https://www.rtr.at/en/tk/E_Commerce_Gesetz for the legal background.
Unfortunately, the only sample code provided by the RTR is in Perl (Boo! Hiss!), which
prompted the creation of this module.


Obtaining the official blacklist
--------------------------------

You will need to follow the steps outlined at https://www.rtr.at/en/tk/NutzenECG
to obtain a copy of the current ECG list. Save the "ecg-liste.hash" you receive
and configure the ECGList to access that file.


Installation
------------

To install this module, simply: ::

	$ pip install email-ecglist


