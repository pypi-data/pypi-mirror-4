#
# Copyright 2012-2013 Corporation of Balclutha (http://www.balclutha.org)
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


from setuptools import setup, find_packages

################################
# These variables are overwritten by Zenoss when the ZenPack is exported
# or saved.  Do not modify them directly here.
# NB: PACKAGES is deprecated
NAME = "ZenPacks.lbn.Base"
VERSION = "4.0.3"
AUTHOR = "Last Bastion Network"
LICENSE = "ZPL/2.1"
NAMESPACE_PACKAGES = ['ZenPacks', 'ZenPacks.lbn']
PACKAGES = ['ZenPacks', 'ZenPacks.lbn', 'ZenPacks.lbn.Base']
INSTALL_REQUIRES = ['lbn.zenoss>=4.2.0']
COMPAT_ZENOSS_VERS = ">=3.0"
PREV_ZENPACK_NAME = ""
# STOP_REPLACEMENTS
################################
# Zenoss will not overwrite any changes you make below here.

def read(name):
    return open(name).read()


long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
    )


setup(name='ZenPacks.lbn.Base',
      version=VERSION,
      description="Base wrappers to save real Zopistas from Zenoss cruft",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Plone",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python",
        "Programming Language :: Zope",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Zope Public License",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        ],
      keywords='lbn zenoss',
      author='Last Bastion Network',
      author_email='alan.milligan@last-bastion.net',
      url='http://linux.last-bastion.net/LBN/up2date/monitor',
      license='ZPL/2.1',
      packages=find_packages(),
      namespace_packages=NAMESPACE_PACKAGES,
      include_package_data=True,
      zip_safe=False,
      install_requires=INSTALL_REQUIRES,
      entry_points="""
      # -*- Entry points: -*-
      [zope2.initialize]
      ZenPacks.lbn.Base = ZenPacks.lbn.Base:initialize
      [zenoss.zenpacks]
      ZenPacks.lbn.Base = ZenPacks.lbn.Base
      """
)
