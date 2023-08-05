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

import zope.interface
import zope.schema


class ISampleDataPlugin(zope.interface.Interface):
    """A plugin that generates some sample data.

    These plugins may depend on other sample data plugins.  Say,
    calendar event generators depend on person generators.  All
    plugins have unique names and other plugins reference their
    dependencies by these names.
    """

    dependencies = zope.schema.List(
        title=u"A list of dependenies",
        value_type=zope.schema.Id(title=u"Sample data generator name"),
        description=u"""
        A list of names of sample data generators this one depends on.
        """)

    schema = zope.schema.InterfaceField(
            title=u"Parameters",
            description=u"The schema which provides the parameters.",
            )

    def validate(context, param, dataSource={}, seed=None):
        """Return True if the plugin can get processed otherwise return one or
        more error messages (str, unicode including HTML).
        """

    def generate(context, param={}, dataSource=None, seed=None):
        """Generate sample data."""

    def cleanup(context, param={}, dataSource=None, seed=None):
        """Cleanup sample data."""


class ISampleManager(zope.interface.Interface):
    """A sample manager manages the generation of sample data.
    
    The manager uses a list of sample generators.
    """

    name = zope.schema.TextLine(
            title = u'Name',
            description = u'The unique name of the sample manager',
            )

    def addSource(name, data):
        """Add a new data source to the manager.

        A data source can be assigned to generator plugins.
        """

    def add(generator,
            param={},
            dataSource=None,
            dependsOn=[],
            contextFrom=None):
        """Add a generator to the manager.

        generator:
            The name of a utility providing 'ISampleDataPlugin'.
        dataSource
            The name of the data source for the generator.
        dependsOn:
            The names of generators this generator depends on.
            This is used in addition to the dependencies defined in the
            generator.
        contextFrom:
            The context for the plugin is the output of this plugin.
            This plugin is automatically used as a dependent plugin.
        """

    def validate(context, param, dataSource={}, seed=None):
        """Return True if the plugin can get processed otherwise return one or
        more error messages (str, unicode including HTML).
        """

    def generate(context=None, param={}, seed=None):
        """Generate the sample data.

        Runs the generate functions of all plugins in an order such that
        the dependencies are all generated before the dependents.

        In essence, this function performs a topological sort in a
        directed acyclic graph.

        Raises a CyclicDependencyError if the dependency graph has a cycle.

        Returns a dict with names of plugins run as keys and CPU times as
        values.

        context:
            The context to be used to generate the sample data.
        param:
            A mapping containing the parameters for the generator plugins.
            The key is the name of the plugin.
        """

    def cleanup(context, param={}, dataSource=None, seed=None):
        """Cleanup sample data."""
