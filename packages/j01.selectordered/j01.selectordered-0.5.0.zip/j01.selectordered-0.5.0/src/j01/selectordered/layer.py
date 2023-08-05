###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""widget layer

"""
__docformat__ = "reStructuredText"

import zope.interface


class IOrderedSelectLayer(zope.interface.Interface):
    """OrderedSelect widget layer also usable for non IBrowserRequest.""" 