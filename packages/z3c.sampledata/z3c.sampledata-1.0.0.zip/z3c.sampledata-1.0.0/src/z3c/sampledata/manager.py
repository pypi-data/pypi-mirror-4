##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""A manager for sample generation.
"""
import time

from zope import interface
from zope import component

from interfaces import ISampleDataPlugin, ISampleManager
from interfaces import CyclicDependencyError


class Manager(object):
    interface.implements(ISampleManager)

    def __init__(self, name, seed):
        self.name = name
        self.seed = seed
        self.generators = {}
        self.sources = {}

    def addSource(self,
                  name,
                  data=None,
                  adaptTo=None,
                  adapterName=u''):
        self.sources[name] = (data, adaptTo, adapterName)

    def add(self,
            generator,
            param={},
            dataSource=None,
            dependsOn=[],
            contextFrom=None):
        info = self.generators.setdefault(generator, {})
        info['param'] = param
        info['dataSource'] = dataSource
        info['dependsOn'] = dependsOn
        info['contextFrom'] = contextFrom

    def orderedPlugins(self):
        # status is a dict plugin names as keys and statuses as values.
        # Statuses can be as follows:
        #
        #   new    -- not yet visited
        #   closed -- already processed
        #   open   -- being processed
        #
        # Stumbling over an 'open' node means there is a cyclic dependency
        new = 'new'
        open = 'open'
        closed = 'closed'
        status = {}

        # plugins contains all plugins to be used including dependent plugins.
        plugins = []
        callstack = []

        def insertPlugin(name):
            """Insert the plugin into plugins including all dependent plugins.

            Builds a calling list of all plugins in the correct order.
            """
            if name in callstack:
                raise CyclicDependencyError("cyclic dependency at '%s'" % name)
            callstack.append(name)
            if name not in status:
                status[name] = new
            if status[name] == new:
                status[name] = open
                info = PluginInfo(name)
                if name in self.generators:
                    pluginInfo = self.generators[name]
                    info.addDependents(pluginInfo['dependsOn'])
                    info.contextFrom = pluginInfo['contextFrom']
                    info.param = pluginInfo['param']
                    info.dataSource = pluginInfo['dataSource']
                    if info.contextFrom is not None:
                        info.addDependents([info.contextFrom])
                generator = component.getUtility(ISampleDataPlugin, name)
                info.generator = generator
                info.addDependents(generator.dependencies)
                for depName in info.dependencies:
                    if depName not in status or status[depName] is not closed:
                        insertPlugin(depName)
                plugins.append(info)
                status[name] = closed
            callstack.pop(-1)

        for name in self.generators.keys():
            insertPlugin(name)
        return plugins

    def generate(self, context=None, param={}, seed=None):
        plugins = self.orderedPlugins()

        # contextFrom contains the return values of the plugins
        contextFrom = {}

        for info in plugins:
            genContext = context
            if info.contextFrom is not None:
                genContext = contextFrom[info.contextFrom]
            start = time.clock()
            data, adapterInterface, adapterName = \
                    self.sources.get(info.dataSource, (None, None, None))
            if data is None and adapterInterface is not None:
                data = component.getAdapter(info.generator,
                                            adapterInterface,
                                            name=adapterName)
            generatorParam = param.get(info.name, None)
            if generatorParam is None:
                generatorParam = info.param

            contextFrom[info.name] = info.generator.generate(
                                        genContext,
                                        param=generatorParam,
                                        dataSource=data,
                                        seed=seed)
            info.time = time.clock() - start

        return plugins


class PluginInfo(object):
    def __init__(self, name):
        self.name = name
        self.param = {}
        self.dataSource = None
        self.dependencies = []
        self.contextFrom = None
        self.generator = None
        self.time = 0.0

    def addDependents(self, dependsOn):
        for dependent in dependsOn:
            if dependent not in self.dependencies:
                self.dependencies.append(dependent)

