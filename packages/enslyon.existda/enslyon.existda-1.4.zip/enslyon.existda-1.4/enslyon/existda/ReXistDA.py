"""ReXistDA.py : Remote eXist Database Adapter product module for Zope."""

# -*- coding: ISO-8859-1 -*-

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


__doc__ = """ReXistDA product module."""

from App.special_dtml import HTMLFile
from App.Dialogs import MessageDialog
from Persistence import Persistent
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

import OFS.SimpleItem
import Acquisition
import AccessControl.Role
from zLOG import LOG, DEBUG

import xmlrpclib, urllib
from xmlrpclib import Binary
from types import StringType

from utils import iseXistURI, isHTTPURI
import eXistDA
import utils
import eXistDAresult
import xslt


## Zope method for management
manage_addReXistDAForm = HTMLFile('dtml/ReXistDAAdd', globals())
def manage_addReXistDA(self, id, title='', server='', port='', username='', password='', encoding=utils.DEFAULT_ENCODING, xmlrpc_path=utils.DEFAULT_ZOPE_XMLRPC_PATH, REQUEST=None):
    """Add an Remote eXist connector object."""
    # Avoid empty encoding
    if encoding.strip() == '':
        encoding = utils.DEFAULT_ENCODING

    msg = utils.getInvalidMsg(server, port, username, password, encoding)
    if msg is None :
        self._setObject(id, ReXistDA(id, title, server, port, username, password, encoding, xmlrpc_path))
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)
    else:
        if REQUEST is not None:
            return msg

# The class which represents an remote eXist "proxy" or database adapter.
class ReXistDA (eXistDA.eXistDA):
    """An Remote eXist connector object."""

    meta_type = utils.REXISTDA_METATYPE

    #__ac_permissions__ = (
    #  (utils.PERM_MANAGE_ACCESS, ('manage_tabs', 'manage_main', 'manage_edit')),
    #  ('Change permissions', ('manage_access')),
    #)


    manage_options = (
      {'label':'Edit', 'action':'manage_main', 'help':('eXistDA','ReXistDA_add.stx')},
      {'label':'Security', 'action':'manage_access'},
    )

    security = ClassSecurityInfo()
    security.declareObjectProtected('View')

    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'manage_tabs', 'manage_main', 'manage_edit')
    security.declareProtected('Change permissions', 'manage_access')

    security.declarePrivate('password')

    index_html = HTMLFile('dtml/index_RDA', globals())
    manage_main = HTMLFile('dtml/ReXistDAEdit', globals())


    def __init__(self, id, title, server='', port=utils.DEFAULT_PORT, username='', password='', encoding=utils.DEFAULT_ENCODING, xmlrpc_path=utils.DEFAULT_ZOPE_XMLRPC_PATH):
        """Class constructor.

* Returns a new object !!

* 'id' : string containing the id of the Zope object created

* 'title' : string containing the title property of the Zope object

* 'server' : remote zope server name which owns the eXistDA object.

* 'port' : port number used by Zope HTTP server. Default is 8080. Ex : '8080'

* 'username' : login of the user on Zope, with access to target eXistDA. Leave empty for guest (for python2.1). Ex: 'my_user'

* 'password' : password of the selected user. Leave empty if none. Ex : '******' ';-)'

* 'encoding' : encoding of the string which are passed and will be returned by eXistDA object. Default is 'ISO-8859-1', if an empty string is passed. Ex : 'UTF-8'

* 'xmlrpc_path' : address of eXistDA object on remote Zope. Ex : '/my/path/existda'"""

        self.id = str(id)
        self.title = str(title)
        self.server = str(server)
        self.port = str(port)
        self.username = str(username)
        self.password = str(password)
        self.encoding = str(encoding)
        self.xmlrpc_path = str(xmlrpc_path)



    security.declarePrivate('_getConnection')
    def _getConnection(self, xmlrpc_path=None):
        """Opens a connection to the remote Zope server if there's no one available.

* Returns the object which is the proxy to the XMLRPC server"""

        if xmlrpc_path == None:
            xmlrpc_path = self.xmlrpc_path

        if self.username.strip() != '' and self.password.strip() != '':
            server = "http://" + self.username + ':' + self.password +'@' + self.server + ":" + self.port + xmlrpc_path
        else:
            server = "http://" + self.server + ":" + self.port + xmlrpc_path

        ## To do : verify that xmlrpc_path points to an eXistDA object.

        return xmlrpclib.ServerProxy(server, encoding=self.encoding)


    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'findXMLRPCAddress')
    def findXMLRPCAddress(self):
        """Dummy method to provide compatibility to eXistDA. Always return "" for ReXistDA."""

        return ""


    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'isOnline')
    def isOnline(self):
        return (self.id, 1)



    security.declareProtected( utils.PERM_WRITE_ACCESS, 'saveDoc' )
    def saveDoc(self, my_doc, doc_uri, overwrite=1, **kws):
        """Save a document in the database.

* Returns 1 if saved, 0 otherwise

* 'my_doc' : an object/URI/string containing the doc

* 'doc_uri' : a string containing the complete URI (server, path and name) of the doc in the DB

* if 'overwrite' == 1 then if there's an existing doc with the same name, it will be overwritten

* 'kws' : dict for any other parameters. See README.txt for recognized parameters"""

        try:
            return self._getConnection().saveDoc(my_doc, doc_uri, overwrite, kws)
        except:
            return 0

        return 0


    security.declareProtected( utils.PERM_READ_ACCESS, 'getFilesFromQuery')
    def getFilesFromQuery(self, query, **kws):
        """**BROKEN SINCE JUNE 2004 SNAPSHOTS -> modify eXist src to make it work**

Executes an XPATH query or an XQuery on the DB.

* Returns a list of string containing the name and full path of files in the DB which matches the query

* 'query' : a object/URI/string containing an XPATH query or an XQuery

* 'kws' : dict for any other parameters. See README.txt and 'query' for recognized parameters"""

        return self._getConnection().getFilesFromQuery(query, kws)


    security.declareProtected( utils.PERM_READ_ACCESS, 'query' )
    def query(self, query, **kws):
        """Execute an XPATH query or an XQuery on the DB.

* Returns a 'eXistDAresultsSet' object containing all the results returned by the query.

* 'query' : an object/URI/string containing an XPATH query or an XQuery

* 'kws' : dict for any other parameters. See 'README.txt' for recognized parameters

  * 'object_only' : cf. 'README.txt'

  * 'variables' : key to a dict containing variables to pass to the xquery"""

        return self._getConnection().query(query, kws)


    security.declareProtected( utils.PERM_READ_ACCESS, 'isCollection' )
    def isCollection(self, resource_name):
        """Determines if 'resource_name' is a collection in the DB or not.

* Returns 1 if 'resource_name' is a collection, 0 otherwise

* 'resource_name' : a string containing the full path and name of the resource to test"""

        self._getConnection().isCollection(resource_name)


    security.declareProtected( utils.PERM_READ_ACCESS, 'isDocument' )
    def isDocument(self, resource_name):
        """Determines if 'resource_name' is a document in the DB or not.

* Returns 1 if 'resource_name' is a document, 0 otherwise

* 'resource_name' : a string containing the full path and name of the resource to test"""

        return self._getConnection().isDocument(resource_name)


    security.declareProtected( utils.PERM_READ_ACCESS, 'getDoc' )
    def getDoc(self, doc_name, xsl='', pretty_print=utils.DEFAULT_PP, **kws):
        """Retrieve a document in the database.

* Returns a string containing the (XSL transformed if suited) XML document.

* 'doc_name' : a string containing the full path and name of an existing document in the DB

* 'xsl' : a string containing the full path and name of an existing XSL document in the DB. If an empty string is passed, no XSLT is done

* 'if pretty_print' == 1, then the returned string is "pretty printed", ie indented. Else, the string is returned as it is saved in the DB

* 'kws' : dict for any other parameters. See README.txt for recognized parameters"""

        return self._getConnection().getDoc(doc_name, xsl, pretty_print, kws)


    security.declareProtected( utils.PERM_READ_ACCESS, 'getDictFromDoc' )
    def getDictFromDoc(self, doc_name):
        """Returns a dictionary which keys are XML tags and values are XML values from the doc.

**WARNING** : for the moment, attributes are ignored and forgotten.

* Returns a python dictionary

* doc_name : a string containing the full path and name of an existing document in the DB"""

        return self._getConnection().getDictFromDoc(doc_name)


    security.declareProtected( utils.PERM_READ_ACCESS, 'listColl' )
    def listColl(self, coll_name=utils.EXIST_ROOT_COLL, recursive=0, full_path=1):
        """Lists the collections contained in collection coll_name.

* Returns a list containing strings which are sub-collections of 'coll_name'

* 'coll_name' : a string containing the base collection, containing the others. If the parameter is not passed, defaults to 'EXIST_ROOT_COLL' (ie '/db')

* if 'recursive' == 0, returned values will be the direct children collections of 'coll_name'. Otherwise, all sub-collections will be recursively returned (even the children of the children)

* if 'full_path' == 1, the full path to the collections is returned (including '/db/...'). Otherwise, the path returned is relative to 'coll_name'"""

        return self._getConnection().listColl(coll_name, recursive, full_path)


    security.declareProtected( utils.PERM_READ_ACCESS, 'listDoc' )
    def listDoc(self, coll_name='', full_path=0):
        """
        Returns the list of all documents contained in collection 'coll_name'.

- 'coll_name' : the name (with complete path) of the collection you want to list the child collections

- 'full_path' : if != 0 returns the full path of the document, otherwise, only the document name
        """

        return self._getConnection().listDoc(coll_name, full_path)


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'xupdate' )
    def xupdate(self, res_name, xupdate_doc, **kws):
        """Issues an XUpdate command to update a document or a whole collection in the database.

- Returns a number > 0 (nb of updates done ?) if AOK or raise an exception if pb

- 'res_name' : the name (with complete path) of a collection or a document

- 'xupdate_doc' : an object/URI/string containing an XUpdate string

- 'kws' : dict for any other parameters. See README.txt for recognized parameters
        """

        return self._getConnection().xupdate(res_name, xupdate_doc, kws)


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'createColl' )
    def createColl(self, coll_name):
        """Creates a new collection in the coll_name collection.

- Returns 1 if no problem. Returns 0 if collection has not been created

- 'coll_name' : string containing the name of the collection to create, with the **FULL** path
        """

        return self._getConnection().createColl(coll_name)


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'delColl' )
    def delColl(self, coll_name) :
        """Deletes a collection and **ALL** what it contains.

- Returns 1 if no problem. Returns 0 if collection has not been deleted

- 'coll_name' : string containing the name of the collection to delete, with the **FULL** path
        """

        return self._getConnection().delColl(coll_name)


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'delDoc' )
    def delDoc(self, doc_name) :
        """Deletes a document of the DB.

- Returns 1 if no problem. Returns 0 if document has not been deleted

- 'doc_name' : string containing the name of the document to delete, with the **FULL** path
        """

        return self._getConnection().delDoc(doc_name)

InitializeClass(ReXistDA)
