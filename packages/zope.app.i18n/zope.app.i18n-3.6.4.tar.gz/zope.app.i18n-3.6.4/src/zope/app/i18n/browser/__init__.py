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
"""Translation Domain Views

$Id: __init__.py 126935 2012-06-18 15:48:16Z tseaver $
"""
__docformat__ = 'restructuredtext'

from zope.i18n.interfaces import ITranslationDomain

class BaseView(object):

    __used_for__ = ITranslationDomain

    def getAllLanguages(self):
        """Get all available languages from the Translation Domain."""
        return self.context.getAllLanguages()
