from zope import interface
from zope import schema
from zope.configuration.fields import GlobalInterface

from z3c.sampledata import _


class ISampleManagerDirective(interface.Interface):
    """Parameters for the sample manager."""

    name = schema.TextLine(
            title = _(u"Name"),
            description = _(u'The unique name of the sample manager'),
            )

    seed = schema.TextLine(
            title = _(u'Seed'),
            description = _(u'The seed for the random generator'),
            required = False,
            default = u''
            )


class IGeneratorSubDirective(interface.Interface):
    """Parameters for the 'generator' subdirective."""

    name = schema.TextLine(
            title = _(u"Name"),
            description = _(u'The unique name of the sample manager'),
            )

    dependsOn = schema.TextLine(
            title = _(u"Dependencies"),
            description = _(u'The generators this generator depends on.\n'
                            u'As space separated list.'),
            default = u'',
            required = False,
            )

    contextFrom = schema.TextLine(
            title = _(u"Context from"),
            description = _(u'Context for the generator is taken from this'
                            u' generator.'),
            default = u'',
            required = False,
            )

    dataSource = schema.TextLine(
            title = _(u"Datasource"),
            description = _(u'The data source for the generator'),
            default = u'',
            required = False,
            )


class IDataSourceSubDirective(interface.Interface):
    """Parameters for the 'datasource' subdirective."""

    name = schema.TextLine(
            title = _(u"Name"),
            description = _(u'The unique name of the datasource'),
            )

    adapterInterface = GlobalInterface(
            title = _(u"Interface"),
            description = _(u'The interface to adapt to'),
            required = True
            )

    adapterName = schema.TextLine(
            title = _(u"Adapter"),
            description = _(u'The name of the adapter providing the data.'),
            required = False,
            default = u''
            )

