"""xslt.py : XSL transformation with local 4Suite or xsltproc in eXistDA"""

# -*- coding: ISO-8859-1 -*-

#    This file is part of eXistDA
#
#    Copyright (C) 2004  Sebastien PILLOZ - Ecole Normale Superieure de Lyon
#
#    This program is free software; you can redistribute it and/or modify
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


__doc__ = """xslt.py : XSL transformation with local 4Suite or xsltproc in eXistDA"""


SCRIPT = "EXISTDA.xslt.py"

import utils
from zLOG import LOG, INFO, DEBUG

try:
    from Ft.Xml.Xslt import Processor
    from Ft.Xml.InputSource import DefaultFactory
    from Ft.Xml import Domlette, cDomlette
    LOG(SCRIPT + ' :', INFO, "4Suite found. External XSLT will be available for eXistDA.")
except:
    LOG(SCRIPT + ' :', INFO, utils.EXC_NO_4SUITE)

import types


def transform(xslStyleSheet, xmlInput, params=None, xsl_base_uri='', apply_xsl=1, encoding=utils.DEFAULT_ENCODING):
    """Performs an XSL transformation of 'xmlInput' with 'xslStyleSheet'. Returns a string containing the result of the XSLT.

* 'xslStyleSheet' : a string or stream containing the XSL to use

* 'xmlInput' : the XML string to be transformed

* 'params' : a dict containing the parameters to be passed to the xsl

* 'xsl_base_uri' : base uri of the XSL. Must be a string

* 'apply_xsl' : set to 1 (default) to apply the XSLT, 0 to return the XML string not transformed"""

    if utils.USE_XSLTPROC and utils.hasXSLTProc():
        return xsltproc(xslStyleSheet, xmlInput, params, xsl_base_uri, encoding)

    if utils.USE_CDOMLETTE:
        dom_model = cDomlette.implementation
    else:
        dom_model = Domlette.implementation

    if apply_xsl == 1 :
        processor = Processor.Processor(implementation=dom_model, stylesheetIncPaths=[xsl_base_uri])

        if utils.isHTTPURI(xslStyleSheet) or utils.isFileURI(xslStyleSheet):
            ma_xsl = DefaultFactory.fromUri(xslStyleSheet, xsl_base_uri)
        elif type(xslStyleSheet) == types.StringType:
            ma_xsl = DefaultFactory.fromString(xslStyleSheet, xsl_base_uri)
        else:
            ma_xsl = DefaultFactory.fromStream(xslStyleSheet, xsl_base_uri)

        processor.appendStylesheet(ma_xsl)

        mon_xml = DefaultFactory.fromString(xmlInput, xsl_base_uri)

        resultat = processor.run(mon_xml, topLevelParams=params)

        return resultat


    return xmlInput

def xsltproc(xsl, xml, params, uri, encoding=utils.DEFAULT_ENCODING):
    """Do the transformation, using xsltproc"""

    from tempfile import NamedTemporaryFile
    from os import popen
    from time import time

    f = NamedTemporaryFile(mode="wt")
    f.write(xml)

    str_params =""
    if params:
        for key in params:
            str_params += "--stringparam %s %s " % (key, params[key])

    f.flush()
    cmd = "xsltproc --novalid --nonet %s %s %s" % (str_params, xsl.split('://',1)[-1], f.name)
    if (utils.DEBUG > 2):
        LOG(SCRIPT, DEBUG, "xsltproc command line is : \n----------\n%s\n----------" % cmd)
    htmlfile = popen(cmd, "r")

    start_time = time()
    html = htmlfile.read()
    while (len(html) == 0) and (time() - start_time < utils.XSLT_TIMEOUT) :
        html = htmlfile.read()

    if htmlfile.close():
        raise('Unable to complete XSLT with xsltproc')

    if (utils.DEBUG > 2):
        LOG(SCRIPT, DEBUG, "xsltproc returned : \n----------\n%s\n----------" % html)

    f.close()
    # xsltproc produces iso-8859-1 code. Reencode with correct encoding.
    try:
        return unicode(html, 'iso-8859-1').encode(encoding)
    except:
        if (utils.DEBUG > 0):
            LOG(SCRIPT, DEBUG, "xsltproc couldn't return correct encoding")
        return html

