# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: interfaces.py 49670 2012-03-21 13:57:41Z sylvain $

from zope import interface


class IField(interface.Interface):
    """A formulator field.
    """


class IForm(interface.Interface):
    """A formulator form.
    """

