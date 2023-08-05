##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.testing import setupstack
import os
import unittest
import manuel.capture
import manuel.doctest
import manuel.testing
import mock

def setUp(test):
    setupstack.setUpDirectory(test)
    setupstack.context_manager(
        test, mock.patch.dict(os.environ, HOME=os.getcwd()))
    setupstack.context_manager(
        test,
        mock.patch('keyring.get_password',
                   side_effect=lambda name, login: name+login+'pw')
        )

def test_suite():
    return unittest.TestSuite((
        #doctest.DocTestSuite(),
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'README.rst', setUp=setUp, tearDown=setupstack.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

