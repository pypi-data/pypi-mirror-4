###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""interfaces

"""
__docformat__ = "reStructuredText"

import zope.schema

import z3c.form.interfaces


class IOrderedSelectWidget(z3c.form.interfaces.IOrderedSelectWidget):
    """Ordered select widget using JQuery in select_ordere_input.pt template"""