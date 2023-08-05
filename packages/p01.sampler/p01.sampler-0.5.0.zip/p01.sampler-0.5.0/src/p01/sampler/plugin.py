###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface

from p01.sampler import interfaces


class SampleDataPlugin(object):
    """Base functionality for sample data plugin with valid validate method."""

    zope.interface.implements(interfaces.ISampleDataPlugin)

    def validate(self, context, param, dataSource={}, seed=None):
        """Allways return True. Override and return a status if needed."""
        return True

    def generate(context, param={}, dataSource=None, seed=None):
        """Generate sample data."""
        raise NotImplementedError("Subclass must implement generate")

    def cleanup(self, context, param, dataSource={}, seed=None):
        """Cleanup sample data"""
        pass
