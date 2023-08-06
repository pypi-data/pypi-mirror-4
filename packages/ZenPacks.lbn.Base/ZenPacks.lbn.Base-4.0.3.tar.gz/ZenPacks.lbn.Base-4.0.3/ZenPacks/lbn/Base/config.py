#
#    Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
from os import path

PROJECTNAME = "ZenPacks.lbn.Base"
# ZenUtils expects full skin path in it's registration lookup
SKINS_DIR = path.join(path.dirname(__file__), 'skins')
SKINNAME = PROJECTNAME
GLOBALS = globals()
