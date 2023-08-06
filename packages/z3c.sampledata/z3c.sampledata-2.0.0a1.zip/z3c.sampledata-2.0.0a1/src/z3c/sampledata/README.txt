===============================
Pluggable sample data framework
===============================

Creating a good testing environment is the most important way to create
high quality software.

But most of the time it is a pain !

This package tries to do the best to support the development of sample
data generators.
A sample data generator is a pluggable tool to create data needed for tests.


There are several goals to this framework:

- provide the developers with an automatic setup that is close to
  real-world use.

- provide the users with an easy setup for evaluation with plausible data

- provide the user a management interface for different sample generators

The framework is pluggable and allows the creators of generator
extensions to provide their own plugins that generate sample data for
those extensions.


Generators
----------

A generator generates sample data.

  >>> from zope import interface
  >>> from zope import component
  >>> from z3c.sampledata.interfaces import ISampleDataPlugin

  >>> @interface.implementer(ISampleDataPlugin)
  ... class GeneratePrincipals(object):
  ...     dependencies = []
  ...     schema = None
  ...     def generate(self, context, param={}, dataSource=None, seed=None):
  ...         print(self.__class__.__name__)
  ...         if dataSource is not None:
  ...             for data in dataSource:
  ...                 print('- %s'%data['login'])
  >>> principalPlugin = GeneratePrincipals()

For our tests we provide another generator :

  >>> @interface.implementer(ISampleDataPlugin)
  ... class GenerateSite(object):
  ...     dependencies = []
  ...     schema = None
  ...     def generate(self, context, param={}, dataSource=None, seed=None):
  ...         if 'sitename' in param:
  ...             print('This is site %r'%param['sitename'])
  ...         else:
  ...             print(self.__class__.__name__)
  ...         return 'I am from the site'
  >>> sitePlugin = GenerateSite()


Generator Manager
-----------------

A generator manager groups a collection of generators.
The manager allows to :

  - define dependencies between generators

  - define data connections between dependent generators

  - provide default configuration data

  >>> from z3c.sampledata import Manager
  >>> manager = Manager('manager', '')


Generator Plugin
~~~~~~~~~~~~~~~~

For the manager our sample generators must be registered as named utilities.

  >>> component.provideUtility(sitePlugin,
  ...                          ISampleDataPlugin,'z3c.sampledata.site')
  >>> component.provideUtility(principalPlugin,
  ...                          ISampleDataPlugin,'z3c.sampledata.principals')


Generating Sample Data
~~~~~~~~~~~~~~~~~~~~~~

Now we can add generators to the manager.

  >>> manager.add('z3c.sampledata.principals',
  ...             dependsOn=['z3c.sampledata.site',],
  ...             contextFrom='z3c.sampledata.site')

In addition to the "hardwired" dependencies defined by the dependencies
property in each generator it is possible to add dependencies in the generator
manager.

A manager provides it's generators.

  >>> list(manager.generators.keys())
  ['z3c.sampledata.principals']

We can tell the manager to generate all samples.
There is no need to add the sample generator 'z3c.sampledata.site', it is added
automatically because of the dependency of 'z3c.sampledata.principals'.

  >>> infos = manager.generate(context=None, param={}, seed='something')
  GenerateSite
  GeneratePrincipals

  >>> [info.name for info in infos]
  ['z3c.sampledata.site', 'z3c.sampledata.principals']


Parameters for the sample generators
------------------------------------

To have more control over the sample generation process it is possible to
setup parameters for the generators.

  >>> manager = Manager('manager', '')

  >>> manager.add('z3c.sampledata.site',
  ...             param={'sitename':'samplesite'})

  >>> manager.add('z3c.sampledata.principals',
  ...             dependsOn=['z3c.sampledata.site',],
  ...             contextFrom='z3c.sampledata.site')

  >>> infos = manager.generate(context=None, param={}, seed='something')
  This is site 'samplesite'
  GeneratePrincipals

It is also possible to overwrite the parameters from the configuration.

  >>> infos = manager.generate(context=None,
  ...                          param={'z3c.sampledata.site':
  ...                                 {'sitename':'managers site'}},
  ...                          seed='something')
  This is site 'managers site'
  GeneratePrincipals


Cycles in the generator definition
----------------------------------

  >>> manager = Manager('manager', '')
  >>> manager.add('z3c.sampledata.principals',
  ...             dependsOn=['z3c.sampledata.site',],
  ...             contextFrom='z3c.sampledata.site')
  >>> manager.add('z3c.sampledata.site',
  ...             dependsOn=['z3c.sampledata.principals',])

  >>> infos = manager.generate(context=None, param={}, seed='something')
  Traceback (most recent call last):
  ...
  CyclicDependencyError: cyclic dependency at 'z3c.sampledata.principals'


A test for a complex dependency.

  >>> @interface.implementer(ISampleDataPlugin)
  ... class Generator(object):
  ...     name = 'generator'
  ...     dependencies = []
  ...     schema = None
  ...     def generate(self, context, param={}, dataSource=None, seed=None):
  ...         return 'I am a generator'
  >>> component.provideUtility(Generator(), ISampleDataPlugin,'g.1')
  >>> component.provideUtility(Generator(), ISampleDataPlugin,'g.2')
  >>> component.provideUtility(Generator(), ISampleDataPlugin,'g.3')
  >>> manager = Manager('manager', '')
  >>> manager.add('g.1')
  >>> manager.add('g.2', contextFrom='g.1')
  >>> manager.add('g.3', dependsOn=['g.2', 'g.1'], contextFrom='g.1')
  >>> infos = manager.generate(context=None, param={}, seed=None)
  >>> [info.name for info in infos]
  ['g.1', 'g.2', 'g.3']


Sample Data Source
------------------

A sample data generator usually gets its sample data from a data source.
Mostly it is necessary to have different data sources for different uses.

As an example, it is always a pain if the sample data for the tests use the
same data as the UI uses later to provide data for the customer to click
around.

  >>> manager = Manager('manager', '')

  >>> manager.addSource('z3c.datasource.principals',
  ...                   data=[{'login':'jukart', 'password':'trakuj'},
  ...                         {'login':'srichter', 'password':'rethcirs'}])

  >>> manager.add('z3c.sampledata.principals',
  ...             dataSource='z3c.datasource.principals',
  ...             dependsOn=['z3c.sampledata.site',],
  ...             contextFrom='z3c.sampledata.site')

  >>> infos = manager.generate(context=None, param={}, seed='something')
  GenerateSite
  GeneratePrincipals
  - jukart
  - srichter


It is also possible to use adapters to act as a data source.

  >>> manager = Manager('manager', '')

  >>> class IPrincipalDataSource(interface.Interface):
  ...     pass

  >>> def principalDataFactory(object):
  ...      return [{'login':'jukart', 'password':'trakuj'},
  ...              {'login':'srichter', 'password':'rethcirs'}]

  >>> component.provideAdapter(
  ...                          factory=principalDataFactory,
  ...                          adapts=(ISampleDataPlugin,),
  ...                          provides=IPrincipalDataSource,
  ...                          name='testprincipals')

  >>> manager.addSource('z3c.datasource.principals',
  ...                   adapterName='testprincipals',
  ...                   adaptTo=IPrincipalDataSource)

  >>> manager.add('z3c.sampledata.principals',
  ...             dataSource='z3c.datasource.principals',
  ...             dependsOn=['z3c.sampledata.site',],
  ...             contextFrom='z3c.sampledata.site')

  >>> infos = manager.generate(context=None, param={}, seed='something')
  GenerateSite
  GeneratePrincipals
  - jukart
  - srichter


How to setup configuration for the generator manager
----------------------------------------------------

Configuration can be done using ZCML::

  <configure xmlns="http://namespaces.zope.org/zope">

    <configure
        xmlns:zcml="http://namespaces.zope.org/zcml"
        zcml:condition="have devmode">

      <utility
          factory=".SampleSite"
          provides="z3c.sampledata.interfaces.ISampleDataPlugin"
          name="z3c.site"
          />

      <utility
          factory=".SamplePrincipals"
          provides="z3c.sampledata.interfaces.ISampleDataPlugin"
          name="z3c.principals"
          />

      <SampleManager
        name="Site with principals"
        >
        <generator name="z3c.site" />
        <generator
          name="z3c.principal"
          dependsOn="z3c.site"
          contextFrom="z3c.site" />
      </SampleManager>

    </configure>

  </configure>


Data Sources
------------

This package implements the base functionality for data generators.
A data generator is used to provide the raw data for a sample generator.
Raw data can be read from text files in different ways.

  >>> from z3c.sampledata.data import DataGenerator
  >>> generator = DataGenerator(55)

The generator can read data lines from files.

  >>> generator.readLines('testlines.txt')
  [u'Line 1', u'Another line']

The generator can read data from CSV files.

  >>> generator.readCSV('testlines.csv')
  [['Line 1', 'Col 2'], ['Another line', 'Another Col']]

The generator can read a list of files from a path :

  >>> import os
  >>> generator.files(os.path.dirname(__file__))
  ['...README.txt', ...]

