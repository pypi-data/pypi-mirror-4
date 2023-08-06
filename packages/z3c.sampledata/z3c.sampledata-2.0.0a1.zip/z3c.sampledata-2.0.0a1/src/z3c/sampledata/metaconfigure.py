###############################################################################
#
# Copyright 2006 by Zope Foundation and Contributors
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""ZCML Directives
"""
from zope.component.zcml import utility

from z3c.sampledata.manager import Manager
from z3c.sampledata.interfaces import ISampleManager


class sampleManager(object):

    def __init__(self,_context, name, seed=''):
        self.manager = Manager(name, seed)
        utility(_context, ISampleManager, component=self.manager, name=name)

    def generator(self, _context,
                  name,
                  dependsOn=None,
                  contextFrom=None,
                  dataSource=None):
        dependencies = []
        if dependsOn is not None:
            dependencies = dependsOn.split()
        self.manager.add(name,
                         dependsOn=dependencies,
                         contextFrom=contextFrom,
                         dataSource=dataSource)

    def datasource(self, _context, name, adapterInterface, adapterName=u''):
        self.manager.addSource(name,
                               data=None,
                               adaptTo=adapterInterface,
                               adapterName=adapterName)


    def __call__(self):
        return
