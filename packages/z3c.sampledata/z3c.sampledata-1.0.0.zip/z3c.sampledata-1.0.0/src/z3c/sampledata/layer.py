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
"""A test layer to use a saved database.

The testlayer creates a database using a sampledata generator and uses the
database for all tests.

WARNING :
    This is work in progress !

TODO:
    Write tests
"""
import os
import transaction

from ZODB.FileStorage import FileStorage

from zope import component
from zope import schema

from zope.app.appsetup import database
from zope.app.testing import functional
from zope.app.publication.zopepublication import ZopePublication

from z3c.sampledata.interfaces import ISampleManager


class BufferedDatabaseTestLayer(object):
    """A test layer which creates a sample database.

    The created database is later used without the need to run through the
    sample generation again.
    This speeds up functional tests.
    """

    __name__ = "BufferedTestLayer"

    __bases__ = (functional.Functional,)

    sampleManager = 'samplesite'
    seed          = 'Seed'
    path          = None

    def setUp(self):
        deleteSet = ' /\\,'
        name = ''.join([c for c in self.sampleManager if c not in deleteSet])
        dbpath = self.path
        dbDirName = 'var_%s' % name
        if dbDirName not in os.listdir(dbpath):
            os.mkdir(os.path.join(dbpath, dbDirName))
        filename = os.path.join(dbpath, dbDirName, 'TestData.fs')

        fsetup = functional.FunctionalTestSetup()
        self.original = fsetup.base_storage

        if not os.path.exists(filename):
            # Generate a new database from scratch and fill it with sample data
            db = database(filename)
            connection = db.open()
            root = connection.root()
            app = root[ZopePublication.root_name]
            # get the sample data manager
            manager = component.getUtility(ISampleManager,
                                           name=self.sampleManager)
            # create the parameters needed
            param = self._createParam(manager)
            # generate the sample data
            manager.generate(app, param, self.seed)
            transaction.commit()
            connection.close()
            db.close()

        # sets up the db stuff normal
        fsetup.setUp()
        # replace the storage with our filestorage
        fsetup.base_storage = FileStorage(filename)
        # override close on this instance, so files dont get closed on
        # setup/teardown of functionsetup
        fsetup.base_storage.close = lambda : None

    def tearDown(self):
        fsetup = functional.FunctionalTestSetup()
        # close the filestorage files now by calling the original
        # close on our storage instance
        FileStorage.close(fsetup.base_storage)
        fsetup.base_storage = self.original
        fsetup.tearDown()
        fsetup.tearDownCompletely()

    def _createParam(self, manager):
        # create the neccessary parameters from the schemas
        ret = {}
        plugins = manager.orderedPlugins()
        for plugin in plugins:
            ret[plugin.name] = data = {}
            iface = plugin.generator.schema
            if iface is not None:
                for name, field in schema.getFieldsInOrder(iface):
                    data[name] = field.default or field.missing_value
        return ret
