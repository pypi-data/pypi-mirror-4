##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Principal Annotation Tests

$Id: tests.py 130063 2013-03-07 19:12:54Z menesis $
"""
import unittest
import doctest

def test_bbb_imports():
    """
    The most of functionality was moved to zope.principalannotation.
    Let's test if old imports still work::
    
      >>> from zope.app.principalannotation.interfaces import IPrincipalAnnotationUtility
      >>> IPrincipalAnnotationUtility
      <InterfaceClass zope.principalannotation.interfaces.IPrincipalAnnotationUtility>
    
      >>> from zope.app.principalannotation import PrincipalAnnotationUtility
      >>> from zope.app.principalannotation import Annotations
      >>> from zope.app.principalannotation import annotations
    
      >>> PrincipalAnnotationUtility
      <class 'zope.principalannotation.utility.PrincipalAnnotationUtility'>

      >>> Annotations
      <class 'zope.principalannotation.utility.Annotations'>

      >>> print annotations.__module__ + '.' + annotations.__name__
      zope.principalannotation.utility.annotations
    
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite()
        ))
