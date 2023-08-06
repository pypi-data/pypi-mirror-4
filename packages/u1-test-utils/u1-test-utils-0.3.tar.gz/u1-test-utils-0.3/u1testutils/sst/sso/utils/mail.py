# -*- coding: utf-8 -*-

# Copyright 2012, 2013 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import quopri
import re

import u1testutils.mail


def _get_verification_data_for_address(email_address):
    """A private helper for public helpers below.

    Note: We have two different public helpers here for verification
    code and link so that functional tests don't need to deal with
    idioms like:
        vcode, ignored = get_verification_for_address(email_address).
    """
    email_msg = u1testutils.mail.get_latest_email_sent_to(email_address)
    vcode = link = None
    if email_msg:
        # The body is encoded as quoted-printable.  This affects any
        # line longer than a certain length.  Decode now to not have
        # to worry about it in the regexen.
        body = quopri.decodestring(email_msg.get_payload())
        match = re.search(
            'Here is your confirmation code:(.*)(Enter|If you made)',
            body, re.S)
        if match:
            vcode = match.group(1).strip()
        else:
            raise AssertionError("No verification code found in email.")
        links = map(str.strip, re.findall('^(http.*)$', body, re.MULTILINE))
        if links:
            link = links[0]
        else:
            msg = "No verification link found in email. Email is:\n%r."
            raise AssertionError(msg % body)
    return vcode, link


def get_verification_code_for_address(email_address):
    print("Retrieving verification code for %s." % email_address)
    vcode, link = _get_verification_data_for_address(email_address)
    print("Verification code retrieved: %s." % vcode)
    return vcode


def get_verification_link_for_address(email_address):
    print("Retrieving verification link for %s." % email_address)
    vcode, link = _get_verification_data_for_address(email_address)
    print("Verification link retrieved: %s." % link)
    return link
