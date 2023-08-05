"""eXistDA.py : eXist Database Adapter product module for Zope."""

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


__doc__ = """eXistDA product module."""

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
import utils
import eXistDAresult
import xslt

import string

## Zope method for management
manage_addeXistDAForm = HTMLFile('dtml/eXistDAAdd', globals())
def manage_addeXistDA(self, id, title='', server='', port='', username='', password='', encoding=utils.DEFAULT_ENCODING, xmlrpc_path=utils.DEFAULT_XMLRPC_PATH, REQUEST=None):
    """Add an eXist connector object."""
    # Avoid empty encoding
    if encoding.strip() == '':
        encoding = utils.DEFAULT_ENCODING

    msg = utils.getInvalidMsg(server, port, username, password, encoding)
    if msg is None :
        self._setObject(id, eXistDA(id, title, server, port, username, password, encoding, xmlrpc_path))
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)
    else:
        if REQUEST is not None:
            return msg


# The class which represents an eXist "proxy" or database adapter.
class eXistDA (OFS.SimpleItem.Item, Persistent, Acquisition.Implicit, AccessControl.Role.RoleManager):
    """An eXist connector object."""

    meta_type = utils.EXISTDA_METATYPE

    manage_options = (
      {'label':'Edit', 'action':'manage_main'},
      {'label':'Security', 'action':'manage_access'},
    )

    security = ClassSecurityInfo()
    security.declareObjectProtected('View')

    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'manage_tabs', 'manage_main', 'manage_edit')
    security.declareProtected('Change permissions', 'manage_access')
    security.declarePrivate('password')
    def __init__(self, id, title, server='', port=utils.DEFAULT_PORT, username='', password='', encoding=utils.DEFAULT_ENCODING, xmlrpc_path=utils.DEFAULT_XMLRPC_PATH):
        """Class constructor.

* Returns a new object !!

* 'id' : string containing the id of the Zope object created

* 'title' : string containing the title property of the Zope object

* 'server' : server name which runs the DB. Should be a complete name and **SHOULD NEVER BE 'LOCALHOST' or '127.0.0.1'** because it may be, sometimes, evaluated from the client within a link. Ex : 'www.mycomputer.org'

* 'port' : port number used by the eXist's XMLRPC server. Default is 8080. Ex : '8080'

* 'username' : login of the user on the DB. Leave empty for guest (for python2.1). Ex: 'my_user'

* 'password' : password of the selected user. Leave empty if none. Ex : '******' ';-)'

* 'encoding' : encoding of the string which are passed and will be returned by the DB. Default is 'ISO-8859-1', if an empty string is passed. Ex : 'UTF-8'

* 'xmlrpc_path' : address of eXist embedded XMLRPC server. Ex : '/xmlrpc'"""

        self.id = str(id)
        self.title = str(title)
        self.server = str(server)
        self.port = str(port)
        self.username = str(username)
        self.password = str(password)
        self.encoding = str(encoding)
        self.xmlrpc_path = str(xmlrpc_path)

    index_html = HTMLFile('dtml/index_DA', globals())
    manage_main = HTMLFile('dtml/eXistDAEdit', globals())

    security.declareProtected(utils.PERM_READ_ACCESS, 'getDA')
    def getDA(self):
        """Returns a reference to the object itself"""
        return self.__of__

    ###############################################################################
    ### XMLRPC & eXist methods

    ## Private methods, users dont have to see them
    security.declarePrivate('_getConnection')
    def _getConnection(self, xmlrpc_path=None):
        """Opens a connection to the eXist server if there's no one available.

* Returns the object which is the proxy to the XMLRPC server"""

        # See why this bugs...
        #if self.connected is None:
        #    server = "http://" + self.server + ":" + self.port + "/exist/xmlrpc"
        #    self.connected = xmlrpclib.ServerProxy(server, encoding=self.encoding)
        if xmlrpc_path == None:
            xmlrpc_path = self.xmlrpc_path

        if self.username.strip() != '' and self.password.strip() != '':
            server = "http://" + self.username + ':' + self.password +'@' + self.server + ":" + self.port + xmlrpc_path
        else:
            server = "http://" + self.server + ":" + self.port + xmlrpc_path

        return xmlrpclib.ServerProxy(server, encoding=self.encoding)

    security.declarePrivate('_serverIsMe')
    def _serverIsMe(self, URI, **kws):
        """Returns 1 if 'URI' "represents" this object.

* 'URI' : a string containing an URI

* 'kws' : dict for any other parameters. See README.txt for recognized parameters"""

        server = utils.getServerNameFromURI(URI)
        if server.find(':') > -1:
            server = server.split(':')[server.count(':') -1].strip()
        if server.find('@') > -1:
            server = server.split('@')[1].strip()
        # if no server name is passed, assume I'm the good one
        if server.strip() == '':
            return 1

        if server.find('.') > -1:
            if server == self.server:
                return 1
        else:
            if server == self.server.split('.')[0]:
                return 1

        return 0


    security.declarePrivate('_getAnythingAsString')
    def _getAnythingAsString(self, my_data, object_only=0):
        """Returns 'my_data' as a string. Raise an error if nothing can be returned. 1 level depth only (ie an HTTP URI in a file will return the HTTP URI, not the string contained in the page at the URI)

* 'my_data' : a string, a file like object, a zope object, an HTTP URI, an eXist URI

* 'object_only' : an integer, which determines if we only do a test for an object (1) or not (0). Useful for URI-like parameters

"""

        try:
            # is my_data a file like object ? Does it have a read method ?
            if hasattr(my_data, 'read'):
                return my_data.read()
            elif hasattr(my_data, 'view_image_or_file'):
                return str(my_data)
        except:
            pass

        if not object_only :
            #try:
                # is my_data a string ?
                if type(my_data) == StringType:
                    # is my_data an HTTP URI ?

                    if isHTTPURI(my_data):
                        return urllib.urlopen(my_data).read()

                    elif iseXistURI(my_data):
                        if self._serverIsMe(my_data, object_only=1):
                            return self.getDoc(my_data, object_only=1)

                        else:
                            return my_data

                    # else, we return the string !
                    else :
                        return my_data

            #except:
                #pass

        else:
            return str(my_data)

        # and the rest ?

        return utils.EXC_NOT_STRING



    ## User's methods (or manager's...)

    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'isOnline')
    def isOnline(self):
        """Determines (by trying a sync() on the DB if the server is online.

* Returns a tuple consisting of the id of the server, and 1 if it's up, 0 if not"""

        try:
            # We do a synchronisation to see if the server is up
            self._getConnection().sync()
            return (self.id, 1)
        except:
            pass

        return (self.id, 0)


    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'findXMLRPCAddress')
    def findXMLRPCAddress(self):
        """Tries to find the address of the eXist XMLRPC embedded server.

* Returns the first address if found, or an empty string if nothing is found."""


        lst_addr = ['/exist/xmlrpc', '/xmlrpc']
        if self.xmlrpc_path:
            lst_addr.insert(0, self.xmlrpc_path)

        valid_addr = ""
        for addr in lst_addr:
            try:
                self._getConnection(addr).sync()
                valid_addr = addr
                break
            except:
                pass

        return valid_addr


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'saveDoc' )
    def saveDoc(self, my_doc, doc_uri, overwrite=1, **kws):
        """Save a document in the database.

* Returns 1 if saved, 0 otherwise

* 'my_doc' : an object/URI/string containing the doc

* 'doc_uri' : a string containing the complete URI (server, path and name) of the doc in the DB

* if 'overwrite' == 1 then if there's an existing doc with the same name, it will be overwritten

* 'kws' : dict for any other parameters. See README.txt for recognized parameters"""

        err = 0

        if kws.has_key(utils.OBJ_ONLY):
            doc_string = self._getAnythingAsString(my_doc, int(kws[utils.OBJ_ONLY]))
        else:
            doc_string = self._getAnythingAsString(my_doc)


        if self._serverIsMe(doc_uri, object_only=1):
            try:
                # To do : overwrite = 0 seems not to work
                err = self._getConnection().parse(Binary(doc_string), utils.getRscNameFromURI(doc_uri), overwrite)
            except:
                import traceback
                traceback.print_exc()
                raise utils.EXC_CANT_SAVE

        else:
            raise utils.EXC_NOT_THIS_DB

        # err is an XMLRPC Boolean... convert it to a 1 or 0
        return err == 1

    security.declareProtected( utils.PERM_WRITE_ACCESS, 'saveDoc' )
    def storeBinary(self, my_doc, doc_uri, overwrite=1, mimetype="application/binary", **kws):
        """Save a binary document in the database.

* Returns 1 if saved, 0 otherwise

* 'my_doc' : an object/URI/string containing the doc

* 'doc_uri' : a string containing the complete URI (server, path and name) of the doc in the DB

* if 'overwrite' == 1 then if there's an existing doc with the same name, it will be overwritten

* 'kws' : dict for any other parameters. See README.txt for recognized parameters"""

        err = 0

        if kws.has_key(utils.OBJ_ONLY):
            doc_string = self._getAnythingAsString(my_doc, int(kws[utils.OBJ_ONLY]))
        else:
            doc_string = self._getAnythingAsString(my_doc)

        if self._serverIsMe(doc_uri, object_only=1):
            try:
                err = self._getConnection().storeBinary(Binary(doc_string), utils.getRscNameFromURI(doc_uri), mimetype,1==1)
            except:
                import traceback
                traceback.print_exc()
                raise utils.EXC_CANT_SAVE

        else:
            raise utils.EXC_NOT_THIS_DB

        # err is an XMLRPC Boolean... convert it to a 1 or 0
        return err == 1



    security.declareProtected( utils.PERM_READ_ACCESS, 'getFilesFromQuery')
    def getFilesFromQuery(self, query, **kws):
        """**BROKEN SINCE JUNE SNAPSHOTS -> modify eXist src to make it work**

Executes an XPATH query or an XQuery on the DB.

* Returns a list of string containing the name and full path of files in the DB which matches the query

* 'query' : a object/URI/string containing an XPATH query or an XQuery

* 'kws' : dict for any other parameters. See README.txt and 'query' for recognized parameters"""

        xmlrpc_server = self._getConnection()

        if kws.has_key(utils.OBJ_ONLY):
            query = self._getAnythingAsString(query, int(kws[utils.OBJ_ONLY]))
        else:
            query = self._getAnythingAsString(query)

        ns = {}
        if kws.has_key(utils.OK_NAMESPACES):
            ns = kws[utils.OK_NAMESPACES]


        if kws.has_key(utils.KEY_VARIABLES):
            result = xmlrpc_server.executeQuery(Binary(query), self.encoding, {utils.KEY_VARIABLES:kws[utils.KEY_VARIABLES], utils.OK_NAMESPACES:ns})
        else:
            res = xmlrpc_server.executeQuery(Binary(query), self.encoding, {utils.OK_NAMESPACES:ns})

        dico_res = xmlrpc_server.querySummary(res)
        xmlrpc_server.releaseQueryResult(res)
        lst_ret = []

        for i in range(0,len(dico_res['documents'])):
            lst_ret.append(dico_res['documents'][i][0])

        return lst_ret


    security.declareProtected( utils.PERM_READ_ACCESS, 'query' )
    def query(self, query, **kws):
        """Execute an XPATH query or an XQuery on the DB.

* Returns a 'eXistDAresultsSet' object containing all the results returned by the query.

* 'query' : an object/URI/string containing an XPATH query or an XQuery

* 'kws' : dict for any other parameters. See 'README.txt' for recognized parameters

  * 'object_only' : cf. 'README.txt'

  * 'variables' : key to a dict containing variables to pass to the xquery"""

        xmlrpc_server = self._getConnection()

        if kws.has_key(utils.OBJ_ONLY) and kws[utils.OBJ_ONLY] == 1 :
            query = self._getAnythingAsString(query, int(kws[utils.OBJ_ONLY]))
        else:
            query = self._getAnythingAsString(query)


        ns = {}
        if kws.has_key(utils.OK_NAMESPACES):
            ns = kws[utils.OK_NAMESPACES]


        if utils.DEBUG >= 1:
            LOG("eXistDA - query :", DEBUG, "Query is :\n%s" % query)

        # do we need to pass some variables to the xquery ?
        if kws.has_key(utils.KEY_VARIABLES):
            result = xmlrpc_server.executeQuery(Binary(query), self.encoding, {utils.KEY_VARIABLES:kws[utils.KEY_VARIABLES], utils.OK_NAMESPACES:ns})
        else:
            result = xmlrpc_server.executeQuery(Binary(query), self.encoding, {utils.OK_NAMESPACES:ns})

        resSet = eXistDAresult.eXistDAresultsSet(encoding=self.encoding)

        if int(xmlrpc_server.getHits(result)) > 0:
            for i in range(int(xmlrpc_server.getHits(result))):
                if kws.has_key(utils.KEY_VARIABLES):
                    resSet.append(eXistDAresult.eXistDAresult(self.getDA(), xmlrpc_server.retrieve(result, i, {utils.OK_ENCODING:self.encoding, utils.KEY_VARIABLES:kws[utils.KEY_VARIABLES], utils.OK_NAMESPACES:ns}).data, '', 1, self.encoding))
                else:
                    resSet.append(eXistDAresult.eXistDAresult(self.getDA(), xmlrpc_server.retrieve(result, i, {utils.OK_ENCODING:self.encoding, utils.OK_NAMESPACES:ns}).data, '', 1, self.encoding))

        if utils.DEBUG >= 1:
            LOG("eXistDA - query :", DEBUG, "Got a resultsSet for %s" % self.server)
            if utils.DEBUG >= 3:
                LOG("eXistDA - query :", DEBUG, "XML result is :\n%s" % str(resSet.getMergedXML()))

        xmlrpc_server.releaseQueryResult(result)
        if utils.DEBUG >= 3:
                LOG("eXistDA - query :", DEBUG, "Returning resultsSet to caller")
        return resSet



    security.declareProtected( utils.PERM_READ_ACCESS, 'isCollection' )
    def isCollection(self, resource_name):
        """Determines if 'resource_name' is a collection in the DB or not.

* Returns 1 if 'resource_name' is a collection, 0 otherwise

* 'resource_name' : a string containing the full path and name of the resource to test"""

        if resource_name.strip() == '':
            return 0

        # the collection name can't have a / at the end
        if resource_name.strip()[-1:] == '/':
            resource_name = resource_name.strip()[:-1]

        if iseXistURI(resource_name):
            resource_name = utils.getRscNameFromURI(resource_name)

        if resource_name.strip()[0] != '/':
            resource_name = "/" + resource_name.strip()

        if resource_name == utils.EXIST_ROOT_COLL:
            return 1

        parent_coll = '/'.join(resource_name.split('/')[:-1]) + '/'
        this_coll = ''.join(resource_name.split('/')[-1:])

        try:
            if this_coll in self._getConnection().getCollectionDesc(parent_coll)['collections']:
                return 1
        except:
            return 0

        return 0


    security.declareProtected( utils.PERM_READ_ACCESS, 'isDocument' )
    def isDocument(self, resource_name):
        """Determines if 'resource_name' is a document in the DB or not.

* Returns 1 if 'resource_name' is a document, 0 otherwise

* 'resource_name' : a string containing the full path and name of the resource to test"""

        try:
            if iseXistURI(resource_name):
                resource_name = utils.getRscNameFromURI(resource_name)

            if self._getConnection().hasDocument(resource_name):
                return 1
        except:
            pass

        return 0

    security.declareProtected( utils.PERM_WRITE_ACCESS, 'moveCol' )
    def moveCol(self, collectionPath, destinationPath, **kws):
        """ Move a collection """
        print "ici"
        if iseXistURI(collectionPath):
            collectionPath_shortname = utils.getRscNameFromURI(collectionPath)
            print "collectionPath",collectionPath
            newdestinationPath_shortname  = utils.getRscNameFromURI('/'.join(destinationPath.split('/')[:-1]))
            print "newdestinationPath",newdestinationPath_shortname
            newName = destinationPath.split('/')[-1]
            print "newName",newName
            res = self._getConnection().moveCollection(collectionPath_shortname, newdestinationPath_shortname, newName)
            print "res",res
            return res
        else:
            return None

    security.declareProtected( utils.PERM_READ_ACCESS, 'getBin' )
    def getBin(self, doc_name, **kws):
        """ REtrieve a binary ressource """
        if iseXistURI(doc_name):
            doc_name_short = utils.getRscNameFromURI(doc_name)
            bin = self._getConnection().getBinaryResource(doc_name_short).data
            return bin
        else:
            return None

    security.declareProtected( utils.PERM_READ_ACCESS, 'getDoc' )
    def getDoc(self, doc_name, xsl='', pretty_print=utils.DEFAULT_PP, **kws):
        """Retrieve a document in the database.

* Returns a string containing the (XSL transformed if suited) XML document.

* 'doc_name' : a string containing the full path and name of an existing document in the DB

* 'xsl' : a string containing the full path and name of an existing XSL document in the DB. If an empty string is passed, no XSLT is done

* 'if pretty_print' == 1, then the returned string is "pretty printed", ie indented. Else, the string is returned as it is saved in the DB

* 'kws' : dict for any other parameters. See README.txt for recognized parameters"""

        if iseXistURI(doc_name):
            doc_name_short = utils.getRscNameFromURI(doc_name)
            params = {}

            if pretty_print == 1:
                params[utils.OK_INDENT] = 'yes'
                params[utils.OK_INDENT_SPACES] = 'yes'
            else:
                params[utils.OK_INDENT] = 'no'
                params[utils.OK_INDENT_SPACES] = 'no'

            params[utils.OK_ENCODING] = self.encoding


            if iseXistURI(xsl):
                if kws.has_key(utils.DICT_STYLESHEET_PARAM):
                    params[utils.OK_STYLESHEET_PARAM] = kws[utils.DICT_STYLESHEET_PARAM]

                xsl_short = '/' + xsl.strip().split('//')[1].split('/',1)[1]
                params[utils.OK_STYLESHEET] = xsl_short

                return self._getConnection().getDocument(doc_name_short, params).data
            elif type(xsl) == StringType and xsl.strip() == '':
                return self._getConnection().getDocument(doc_name_short, params).data
            else:
                ma_xsl = self._getAnythingAsString(xsl)
                mon_xml = self._getAnythingAsString(doc_name)
                if utils.DEBUG > 2:
                    LOG('eXistDA - getDoc', DEBUG, "xsl is : %s\n\n xml is %s\n" % (ma_xsl, mon_xml))
                return xslt.transform(ma_xsl, mon_xml, encoding=self.encoding)

        # the doc isn't on an eXist DB
        else:
            params = None
            xsl_base_uri = ''
            if kws.has_key(utils.DICT_STYLESHEET_PARAM):
                params = kws[utils.DICT_STYLESHEET_PARAM]
            if kws.has_key(utils.DICT_STYLESHEET_BASE_URI):
                xsl_base_uri = kws[utils.DICT_STYLESHEET_BASE_URI]

            ma_xsl = xsl
            if kws.has_key(utils.OBJ_ONLY):
                mon_xml = self._getAnythingAsString(doc_name, object_only=kws[utils.OBJ_ONLY])
            else:
                mon_xml = self._getAnythingAsString(doc_name)

            return xslt.transform(ma_xsl, mon_xml, params, xsl_base_uri=xsl_base_uri, encoding=self.encoding)


        #else:
        #    raise utils.EXC_DOC_MUST_BE_ON_EXIST_SERVER



    security.declareProtected( utils.PERM_READ_ACCESS, 'getDictFromDoc' )
    def getDictFromDoc(self, doc_name):
        """Returns a dictionary which keys are XML tags and values are XML values from the doc.

**WARNING** : for the moment, attributes are ignored and forgotten.

* Returns a python dictionary

* doc_name : a string containing the full path and name of an existing document in the DB"""

        if iseXistURI(doc_name) :
            doc = self.getDoc(doc_name, xsl='')
        else:
            doc = self._getAnythingAsString(doc_name)


        if doc.strip() != '':
            dict = utils.getDict(doc, self.encoding)
            return dict

        return {}



    security.declareProtected( utils.PERM_READ_ACCESS, 'listColl' )
    def listColl(self, coll_name=utils.EXIST_ROOT_COLL, recursive=0, full_path=1):
        """Lists the collections contained in collection coll_name.

* Returns a list containing strings which are sub-collections of 'coll_name'

* 'coll_name' : a string containing the base collection, containing the others. If the parameter is not passed, defaults to 'EXIST_ROOT_COLL' (ie '/db')

* if 'recursive' == 0, returned values will be the direct children collections of 'coll_name'. Otherwise, all sub-collections will be recursively returned (even the children of the children)

* if 'full_path' == 1, the full path to the collections is returned (including '/db/...'). Otherwise, the path returned is relative to 'coll_name'"""


        liste_def=[]

        if iseXistURI(coll_name):
            coll_name = utils.getRscNameFromURI(coll_name)

        if coll_name.strip()[-1:] != '/':
            coll_name = coll_name.strip() + "/"

        if recursive == 0:
            liste_coll = self._getConnection().getCollectionDesc(coll_name)['collections']

            if full_path == 1:
                for une_coll in liste_coll:
                    liste_def.append(coll_name + une_coll + '/')
            else:
                return liste_coll

        else:
            liste_def.append(coll_name)
            desc = self._getConnection().getCollectionDesc(coll_name)

            if desc != None:
                for collection in desc['collections']:
                    liste_def = liste_def + self.listColl(coll_name + collection + '/', recursive, full_path)

        return liste_def

    security.declareProtected( utils.PERM_READ_ACCESS, 'listDoc' )
    def listDoc(self, coll_name='', full_path=0):
        """
        Returns the list of all documents contained in collection 'coll_name'.

- 'coll_name' : the name (with complete path) of the collection you want to list the child collections

- 'full_path' : if != 0 returns the full path of the document, otherwise, only the document name
        """

        if iseXistURI(coll_name):
            coll_name = utils.getRscNameFromURI(coll_name)

        xmlrpc_server = self._getConnection()

        if coll_name.strip() != '':
            if coll_name[-1:] != '/':
                coll_name = coll_name + '/'

            liste_tmp = xmlrpc_server.getDocumentListing(coll_name)
        else:
            liste_tmp =  xmlrpc_server.getDocumentListing()

        if coll_name == '' :
            coll_name = utils.EXIST_ROOT_COLL

        if full_path == 0 :
            liste = liste_tmp
        else:
            liste = []
            for item in liste_tmp:
                liste.append(coll_name + item)

        return liste


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'xupdate' )
    def xupdate(self, res_name, xupdate_doc, **kws):
        """Issues an XUpdate command to update a document or a whole collection in the database.

- Returns a number > 0 (nb of updates done ?) if AOK or raise an exception if pb

- 'res_name' : the name (with complete path) of a collection or a document

- 'xupdate_doc' : an object/URI/string containing an XUpdate string

- 'kws' : dict for any other parameters. See README.txt for recognized parameters
        """

        xmlrpc_server = self._getConnection()

        if kws.has_key(utils.OBJ_ONLY):
            xupdate_doc = self._getAnythingAsString(xupdate_doc, int(kws[utils.OBJ_ONLY]))
        else:
            xupdate_doc = self._getAnythingAsString(xupdate_doc)

        if iseXistURI(res_name):
            res_name = utils.getRscNameFromURI(res_name)

        if self.isCollection(res_name):
            # workaround cause there's no encoding choice for xupdate RPC API function...
            xupdate_doc = utils.convert(xupdate_doc, self.encoding, 'UTF-8')

            return xmlrpc_server.xupdate(res_name, Binary(xupdate_doc))
        elif self.isDocument(res_name):
            return xmlrpc_server.xupdateResource(res_name, Binary(xupdate_doc),self.encoding)
        else:
            raise utils.EXC_NOT_RESOURCE

        return 0


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'createColl' )
    def createColl(self, coll_name):
        """Creates a new collection in the coll_name collection.

- Returns 1 if no problem. Returns 0 if collection has not been created

- 'coll_name' : string containing the name of the collection to create, with the **FULL** path
        """

        if iseXistURI(coll_name):
            coll_name = utils.getRscNameFromURI(coll_name)

        try:
            if self._getConnection().createCollection(coll_name):
                return 1
        except:
            return 0

        return 0


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'delColl' )
    def delColl(self, coll_name) :
        """Deletes a collection and **ALL** what it contains.

- Returns 1 if no problem. Returns 0 if collection has not been deleted

- 'coll_name' : string containing the name of the collection to delete, with the **FULL** path
        """

        if coll_name[-1:] == '/':
            coll_name = coll_name[:-1]

        try:
            if self._getConnection().removeCollection(coll_name):
                return 1
        except:
            return 0

        return 0

    security.declareProtected( utils.PERM_WRITE_ACCESS, 'delDoc' )
    def delDoc(self, doc_name) :
        """Deletes a document of the DB.

- Returns 1 if no problem. Returns 0 if document has not been deleted

- 'doc_name' : string containing the name of the document to delete, with the **FULL** path
        """

        if iseXistURI(doc_name):
            doc_name = utils.getRscNameFromURI(doc_name)

        try:
            if self._getConnection().remove(doc_name):
                return 1
        except:
            return 0

        return 0

    security.declareProtected(  utils.PERM_WRITE_ACCESS, 'delRsc' )
    def delRsc(self, rsc_name) :
        """Wrapper to delColl or delDoc. Automatically chooses the good one (TM)

- Returns 1 if no problem. Returns 0 if resource has not been deleted

- 'rsc_name' : string containing the name of a document or collection that must be deleted, with the **FULL** path"""

        if iseXistURI(rsc_name):
            rsc_name = utils.getRscNameFromURI(rsc_name)

        if self.isCollection(rsc_name):
            return self.delColl(rsc_name)
        elif self.isDocument(rsc_name):
            return self.delDoc(rsc_name)

        return 0



    ## End XMLRPC & eXist methods
    ##########################################################################################

    security.declareProtected( utils.PERM_MANAGE_ACCESS, 'manage_edit' )
    def manage_edit(self, title="", server="", port=utils.DEFAULT_PORT, username="", password="", encoding=utils.DEFAULT_ENCODING, xmlrpc_path=utils.DEFAULT_XMLRPC_PATH, REQUEST=None):
        """Change values of object's parameters. (see '__init__')"""
        self.title = str(title)

        # Avoid empty encoding
        if encoding.strip() == '':
            encoding = utils.DEFAULT_ENCODING

        msg = utils.getInvalidMsg(server, port, username, password, encoding)

        if msg is None:

            self.server = str(server).strip()
            self.port = str(port).strip()
            self.username = str(username).strip()
            self.password = str(password).strip()
            self.encoding = str(encoding).strip()
            self.xmlrpc_path = str(xmlrpc_path).strip()



            if REQUEST is not None:
                return MessageDialog(
                    title = 'Edited',
                    message = "Properties for %s changed." % self.id,
                    action = './manage_main',
                    )

        else:
            if REQUEST is not None:
                return msg


    security.declareProtected( utils.PERM_READ_ACCESS, 'fastquery' )
    def fastquery(self, query, start, nbmax, **kws):
        """Execute an XPATH query or an XQuery on the DB.

        * Returns a 'eXistDAresultsSet' object containing all the results returned by the query.

        * 'query' : an object/URI/string containing an XPATH query or an XQuery

        * 'kws' : dict for any other parameters. See 'README.txt' for recognized parameters

        * 'object_only' : cf. 'README.txt'

        * 'variables' : key to a dict containing variables to pass to the xquery"""

        xmlrpc_server = self._getConnection()

        if kws.has_key(utils.OBJ_ONLY) and kws[utils.OBJ_ONLY] == 1 :
            query = self._getAnythingAsString(query, int(kws[utils.OBJ_ONLY]))
        else:
            query = self._getAnythingAsString(query)

        ns = {}
        if kws.has_key(utils.OK_NAMESPACES):
            ns = kws[utils.OK_NAMESPACES]

        if utils.DEBUG >= 1:
            LOG("eXistDA - query :", DEBUG, "Query is :\n%s" % query)

        # do we need to pass some variables to the xquery ?
        if kws.has_key(utils.KEY_VARIABLES):
            result = xmlrpc_server.query(Binary(query), nbmax, start, {utils.KEY_VARIABLES:kws[utils.KEY_VARIABLES], utils.OK_NAMESPACES:ns})
        else:
            result = xmlrpc_server.query(Binary(query), nbmax, start, {utils.OK_NAMESPACES:ns})


        # replace invalid header result if not result
        res = string.replace(result.data, '<?xml version="1.0"?>', '')
        if utils.DEBUG >= 1:
            LOG("eXistDA - query :", DEBUG, "Got a resultsSet for %s" % self.server)
            if utils.DEBUG >= 3:
                LOG("eXistDA - query :", DEBUG, "XML result is :\n%s" % str(resSet.getMergedXML()))


        if utils.DEBUG >= 3:
                LOG("eXistDA - query :", DEBUG, "Returning resultsSet to caller")
        # return raw xml data set
        return res

InitializeClass(eXistDA)
