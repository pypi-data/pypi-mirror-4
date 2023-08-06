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
# with this program.  If not, see <http://www.gnu.org/licenses/

import unittest

from django.conf import settings

from u1testutils.sst.sso import data


class DataTestCase(unittest.TestCase):

    def test_make_exising_user(self):
        # The DJANGO_SETTINGS_MODULE is set by the test fab task.
        user = data.User.make_from_configuration()
        self.assertEqual(user.full_name, settings.SSO_TEST_ACCOUNT_FULL_NAME)
        self.assertEqual(user.email, settings.SSO_TEST_ACCOUNT_EMAIL)
        self.assertEqual(user.password, settings.SSO_TEST_ACCOUNT_PASSWORD)
