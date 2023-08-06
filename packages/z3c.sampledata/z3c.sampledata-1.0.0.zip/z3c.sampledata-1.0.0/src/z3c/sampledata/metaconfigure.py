from zope.component.zcml import utility

from manager import Manager
from interfaces import ISampleManager


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
