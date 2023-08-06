# -*- coding: utf-8 -*-

# Copyright 2013 Canonical Ltd.
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

import email.parser
import unittest

import mock

from u1testutils.sst.sso.utils import mail


class SSOMailTestCase(unittest.TestCase):

    verification_email = email.parser.Parser().parsestr(
        'Content-Type: text/plain; charset="utf-8"\n'
        'MIME-Version: 1.0\n'
        'Content-Transfer-Encoding: quoted-printable\n'
        'Subject: Ubuntu Single Sign On: Finish your registration\n'
        'From: Ubuntu Single Sign On <noreply@ubuntu.com>\n'
        'To: to@example.com\n'
        '\n'
        'Hello\n'
        '\n'
        'As a final step of the Ubuntu Single Sign On (SSO) account '
        'creation process=\n'
        ', please validate the email address to@example.com. Ubuntu SSO '
        'enables conv=\n'
        'enient access to a variety of Ubuntu-related services like Ubuntu '
        'One with =\n'
        'the same username and password.\n'
        '\n'
        'Here is your confirmation code:\n'
        '\n'
        'QM9CSR\n'
        '\n'
        'Enter this code into the registration form, or click the following '
        'link to =\n'
        'automatically confirm your account:\n'
        '\n'
        'https://login.ubuntu.com/confirm-account/QM9CSR/to@example.com\n'
        '\n'
        'If you don\'t know what this is about, then someone has probably '
        'entered you=\n'
        'r email address by mistake. Sorry about that.\n'
        'If you wish to report this email being incorrectly used, please '
        'click the f=\n'
        'ollowing link:\n'
        '\n'
        'https://login.ubuntu.com/invalidate-email/42FcJG/to@example.com\n'
        '\n'
        'You can also seek further assistance on:\n'
        '\n'
        'https://forms.canonical.com/sso-support/\n'
        '\n'
        'Thank you,\n'
        '\n'
        'The Ubuntu Single Sign On team\n'
        'https://login.ubuntu.com/\n'
    )

    def setUp(self):
        super(SSOMailTestCase, self).setUp()
        patcher = mock.patch('u1testutils.mail')
        mock_mail = patcher.start()
        mock_mail.get_latest_email_sent_to.return_value = \
            self.verification_email
        self.addCleanup(patcher.stop)

    def test_get_verification_code(self):
        verification_code = mail.get_verification_code_for_address(
            'to@example.com')
        self.assertEquals(verification_code, 'QM9CSR')

    def test_get_verification_link(self):
        verification_link = mail.get_verification_link_for_address(
            'to@example.com')
        self.assertEquals(
            verification_link,
            'https://login.ubuntu.com/confirm-account/QM9CSR/to@example.com')
