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

import uuid

from django.conf import settings


class User(object):

    def __init__(self, full_name, email, password):
        self.full_name = full_name
        self.email = email
        self.password = password

    def __repr__(self):
        return '%s(%r)' % (self.__class__, self.__dict__)

    @classmethod
    def make_from_configuration(cls, new_user=False):
        """Return a user taking its credentials from the configuration files.

        Keyword arguments:
        new_user -- If True, the full name and email of the user will have a
            UUID to make them practically unique. In this case, the email will
            be formed with the value of the EMAIL_ADDRESS_PATTERN
            configuration variable. If False, the full name and email will be
            the values of the SSO_TEST_ACCOUNT_FULL_NAME and
            SSO_TEST_ACCOUNT_EMAIL configuration variables, respectively. In
            both cases, the password will be the value of the
            SSO_TEST_ACCOUNT_PASSWORD configuration variable.
            Default is False.

        """
        if new_user:
            random_user_uuid = str(uuid.uuid1())
            full_name = 'Test user ' + random_user_uuid
            email = settings.EMAIL_ADDRESS_PATTERN % random_user_uuid
        else:
            full_name = settings.SSO_TEST_ACCOUNT_FULL_NAME
            email = settings.SSO_TEST_ACCOUNT_EMAIL
        password = settings.SSO_TEST_ACCOUNT_PASSWORD
        return cls(full_name, email, password)
