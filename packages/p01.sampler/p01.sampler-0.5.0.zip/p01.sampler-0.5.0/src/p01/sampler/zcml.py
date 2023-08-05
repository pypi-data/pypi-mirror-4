###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

from zope.component.zcml import utility


import zope.interface
import zope.schema
import zope.component.zcml
import zope.configuration.fields

from p01.sampler import interfaces
from p01.sampler import manager


class ISampleManagerDirective(zope.interface.Interface):
    """Parameters for the sample manager."""

    name = zope.schema.TextLine(
            title = u'Name',
            description = u'The unique name of the sample manager',
            )

    seed =  zope.schema.TextLine(
            title = u'Seed',
            description = u'The seed for the random generator',
            required = False,
            default = u''
            )


class IGeneratorSubDirective(zope.interface.Interface):
    """Parameters for the 'generator' subdirective."""

    name =  zope.schema.TextLine(
            title = u'Name',
            description = u'The unique name of the sample manager',
            )

    dependsOn =  zope.schema.TextLine(
            title = u'Dependencies',
            description = u'The generators this generator depends on.\n'
                          u'As space separated list.',
            default = u'',
            required = False,
            )

    contextFrom =  zope.schema.TextLine(
            title = u'Context from',
            description = u'Context for the generator is taken from this '
                          u'generator.',
            default = u'',
            required = False,
            )

    dataSource =  zope.schema.TextLine(
            title = u'Datasource',
            description = u'The data source for the generator',
            default = u'',
            required = False,
            )


class IDataSourceSubDirective(zope.interface.Interface):
    """Parameters for the 'datasource' subdirective."""

    name =  zope.schema.TextLine(
            title = u'Name',
            description = u'The unique name of the datasource',
            )

    adapterInterface = zope.configuration.fields.GlobalInterface(
            title = u'Interface',
            description = u'The interface to adapt to',
            required = True
            )

    adapterName =  zope.schema.TextLine(
            title = u'Adapter',
            description = u'The name of the adapter providing the data.',
            required = False,
            default = u''
            )


class sampleManager(object):

    def __init__(self,_context, name, seed=''):
        self.manager = manager.Manager(name, seed)
        zope.component.zcml.utility(_context, interfaces.ISampleManager,
            component=self.manager, name=name)

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
