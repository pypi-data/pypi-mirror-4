##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Tests for the Preferences System
"""
import doctest
import re
import zope.component.hooks
import zope.component.testing
import zope.testing.module
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    # Python 3 unicode removed the "u".
    (re.compile("u('.*?')"),
     r"\1"),
    (re.compile('u(".*?")'),
     r"\1"),
    # Python 3 adds module name to exceptions.
    (re.compile("zope.security.interfaces.NoInteraction"),
     r"NoInteraction"),
    ])

def addUtility(sitemanager, utility, iface=None, name='', suffix=''):
    folder_name = (name or (iface.__name__ + 'Utility')) + suffix
    default = sitemanager['default']
    default[folder_name] = utility
    utility = default[folder_name]
    sitemanager.registerUtility(utility, iface, name)
    return utility

def setUp(test):
    zope.component.testing.setUp(test)
    zope.component.hooks.setHooks()

    # Traversal
    from zope.traversing.testing import setUp as traversalSetUp
    from zope.traversing.interfaces import ITraversable
    from zope.container.interfaces import ISimpleReadContainer
    from zope.container.traversal import ContainerTraversable
    traversalSetUp()
    zope.component.provideAdapter(ContainerTraversable,
                                  (ISimpleReadContainer,), ITraversable)

    # ISiteManager lookup
    from zope.site.site import SiteManagerAdapter
    from zope.component.interfaces import IComponentLookup
    from zope.interface import Interface
    zope.component.provideAdapter(SiteManagerAdapter, (Interface,),
                                  IComponentLookup)

    # Folder Structure
    from zope.site.folder import Folder, rootFolder
    root = rootFolder()
    test.globs['root'] = root
    root[u'folder1'] = Folder()

    # MAke root a site.
    from zope.site.site import LocalSiteManager
    rsm = LocalSiteManager(root)
    test.globs['rsm'] = rsm
    root.setSiteManager(rsm)
    from zope.site.hooks import setSite
    setSite(root)

    test.globs['addUtility'] = addUtility
    zope.testing.module.setUp(test, 'zope.preference.README')


def tearDown(test):
    zope.component.testing.tearDown(test)
    zope.testing.module.tearDown(test)


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE | \
                    doctest.ELLIPSIS | \
                    doctest.IGNORE_EXCEPTION_DETAIL,
        checker=checker)
