##############################################################################
#
# Copyright (c) 2006-2010 Zope Foundation and Contributors.
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
# $Id: __init__.py 122220 2011-07-14 13:26:32Z janwijbrand $ $Rev$ $Author$ $Date$
"""A functional test layer.
"""
import grokcore.chameleon
from zope.app.wsgi.testlayer import BrowserLayer

FunctionalLayer = BrowserLayer(grokcore.chameleon, 'ftesting.zcml')
