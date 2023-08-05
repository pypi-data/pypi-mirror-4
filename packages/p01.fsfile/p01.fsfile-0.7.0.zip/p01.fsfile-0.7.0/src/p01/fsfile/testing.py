##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.component
import persistent.interfaces
from zope.keyreference.persistent import connectionOfPersistent

###############################################################################
#
# setup helper
#
###############################################################################

def setUpConnection(test=None):
    zope.component.provideAdapter(connectionOfPersistent,
        (persistent.interfaces.IPersistent,))


###############################################################################
#
# Doctest setup
#
###############################################################################

def doctestSetUp(test):
    setUpConnection(test)

def doctestTearDown(test):
    pass

