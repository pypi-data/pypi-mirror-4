#
#    Copyright 2010-2013 Corporation of Balclutha (http://www.balclutha.org)
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
import logging
from Acquisition import aq_base
from lbn.zenoss.packutils import addZenPackObjects
from config import PROJECTNAME

logger = logging.getLogger(PROJECTNAME)
info = logger.info

ZENPACKS = (
    ('ZenPacks.lbn.Base', """Last Bastion Network shims for Zenoss"""),
    ('ZenPacks.lbn.ZopeMonitor', """Performance statistics of (remote) Zope server"""),
    ('ZenPacks.lbn.LDAPMonitor', """Performance statistics of (remote) LDAP server"""),
    ('ZenPacks.oie.Kannel', """Performance statistics of (remote) Kannel SMPP/SMSC server"""),
    )

def addBranding(dmd, zenpack):
    """
    Add LBN Manufacturer/Software into Zenoss
    """
    manufacturers = dmd.Manufacturers

    if not getattr(aq_base(manufacturers), 'LBN', None):
        info('adding Manufacturer - LBN')
        manufacturers.manage_addProduct['ZenModel'].manage_addManufacturer('LBN')
        manufacturers.LBN.manage_changeProperties(url='http://au.last-bastion.net',
                                                  supportNumber='+61 2 8399 1271',
                                                  address1='407 The Foundry, 181 Lawson Street',
                                                  address2='Darlington',
                                                  city='Sydney',
                                                  state='NSW',
                                                  country='Australia',
                                                  zip='2008')

    lbn = manufacturers.LBN
    products = lbn.products

    for packname, desc in ZENPACKS:
        if not getattr(aq_base(products), packname, None):
            info('adding product - %s' % packname)
            lbn.manage_addSoftware(prodName=packname)
            getattr(products, packname).manage_changeProperties(description=desc)

    if not getattr(aq_base(products), 'BastionLinux', None):
        info('adding software - BastionLinux')
        lbn.manage_addSoftware(prodName='BastionLinux', isOS=True)
        bl = products.BastionLinux
        bl.manage_changeProperties(description="Enterprise Zope/Plone/Zenoss Distro http://linux.last-bastion.net")

    addZenPackObjects(zenpack, (lbn,))
