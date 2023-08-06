# -*- extra stuff goes here -*-
"""__init.py__ : eXistDA and eXistDAsyn initialization module."""

# -*- coding: utf-8 -*-

#    This file is part of eXistDA.
#
#    Copyright (C) 2004  Sebastien PILLOZ - Ecole Normale Superieure de Lyon
#
#    eXistDA is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

__doc__ = """eXistDA, ReXistDA and eXistDAsyn initialization module."""

import eXistDA, eXistDAsyn, ReXistDA

def initialize(context):
    """Initializer called when used as a Zope 2 product.

    Initialization of the two classes used to instanciate the two kind of objects seen by zope : eXistDA and eXistDAsyn."""
    try:
        # register the DA
        context.registerClass (
          eXistDA.eXistDA,
          constructors = (
            eXistDA.manage_addeXistDAForm,
            eXistDA.manage_addeXistDA),
          icon='images/eXistDA.png'
        )
        # register the syndicator
        context.registerClass (
          eXistDAsyn.eXistDAsyn,
          constructors = (
            eXistDAsyn.manage_addeXistDAsynForm,
            eXistDAsyn.manage_addeXistDAsyn),
          icon='images/eXistDAsyn.png'
        )
        # register the remote DA
        context.registerClass (
          ReXistDA.ReXistDA,
          constructors = (
            ReXistDA.manage_addReXistDAForm,
            ReXistDA.manage_addReXistDA),
          icon='images/ReXistDA.png'
        )

        context.registerHelp()


    except:
        import sys, traceback, string
        type, val, tb = sys.exc_info()
        sys.stderr.write(string.join(traceback.format_exception(type, val, tb), ''))
        del type, val, tb


import eXistDAresult
from AccessControl import allow_class
allow_class(eXistDAresult.eXistDAresult)
allow_class(eXistDAresult.eXistDAresultsSet)
