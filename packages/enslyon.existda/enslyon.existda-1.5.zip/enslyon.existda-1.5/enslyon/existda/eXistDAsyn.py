"""eXistDAsyn.py : eXistDA Syndicator product module."""

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

__doc__ = """eXistDAsyn product module."""

from App.special_dtml import HTMLFile, DTMLFile
from App.Dialogs import MessageDialog
from Persistence import Persistent
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from zLOG import LOG, DEBUG, INFO

import OFS.SimpleItem, OFS.ObjectManager
import Acquisition, App
import AccessControl.Role
import xmlrpclib, types
import utils
from utils import iseXistURI, isHTTPURI
import eXistDA
import eXistDAresult

## Zope methods for management
manage_addeXistDAsynForm = HTMLFile('dtml/eXistDAsynAdd', globals())
def manage_addeXistDAsyn(self, id, title='', encoding=utils.DEFAULT_ENCODING, REQUEST=None):
    """Add an eXist syndicator object."""

    # Avoid empty encoding
    if encoding.strip() == '':
        encoding = utils.DEFAULT_ENCODING

    self._setObject(id, eXistDAsyn(id, title, encoding))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class eXistDAsyn (OFS.ObjectManager.ObjectManager, Persistent, Acquisition.Implicit, AccessControl.Role.RoleManager, App.Management.Navigation):
    """An eXist syndicator object, containing many eXistDA objects."""

    meta_type = utils.EXISTDASYN_METATYPE

    isAnObjectManager=1

    manage_options =  OFS.ObjectManager.ObjectManager.manage_options + (
      {'label':'Properties', 'action':'manage_properties'},
      {'label':'Security', 'action':'manage_access'},
    )


    security = ClassSecurityInfo()
    security.declareObjectProtected("View")

    security.declareProtected('View management screens', 'manage_tabs', 'manage_main', 'manage_edit')
    security.declareProtected('Change permissions', 'manage_access')

    # Methods to create an eXistDA object in the syndicator
    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'addeXistDA')
    addeXistDA = eXistDA.manage_addeXistDAForm

    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'manage_addeXistDA')
    manage_addeXistDA = eXistDA.manage_addeXistDA
    ###########

    def __init__(self, id, title, encoding=utils.DEFAULT_ENCODING):
        """Initialization of the eXistDAsyn object."""
        self.id = str(id)
        self.title = str(title)
        self.encoding = str(encoding)


    index_html = HTMLFile('dtml/index_syn', globals())
    manage_main = OFS.ObjectManager.ObjectManager.manage_main
    manage_workspace = OFS.ObjectManager.ObjectManager.manage_workspace
    manage_properties = HTMLFile('dtml/eXistDAsynEdit', globals())

    meta_types = [{ 'name' : utils.EXISTDA_METATYPE, 'action' : 'addeXistDA', 'permission' : 'Add eXistDA' }]
    all_meta_types = meta_types

    ###################
    ### Internal methods

    security.declarePrivate('_findServerByURI')
    def _findServerByURI(self, URI):
        """Find the corresponding DA in the syndicator by its URI.

* if a corresponding DA is found, returns the object. Else returns 'None'

* 'URI' : the string containing the URI to test"""

        if utils.iseXistURI(URI):
            # we get the servername and the port number
            try:
                svrname,port = utils.getServerNameFromURI(URI).split(':')
                for DA in self.objectValues([utils.EXISTDA_METATYPE]):
                    if DA.server == svrname and DA.port == port and self.restrictedTraverse(DA.id) != None :
                        return DA
            except:
                svrname= utils.getServerNameFromURI(URI)
                for DA in self.objectValues([utils.EXISTDA_METATYPE]):
                    if DA.server == svrname :
                        return DA

        return None

    security.declarePrivate('_findServerById')
    def _findServerById(self, id):
        """Find the corresponding DA in the syndicator by its id.

* if a corresponding DA is found, returns the object. Else returns 'None'

* 'id' : the string containing the id to test"""

        for DA in self.objectValues([utils.EXISTDA_METATYPE]):
            if DA.id == id:
                return DA

        return None


    security.declarePrivate('_getIteratedServers')
    def _getIteratedServers(self, my_items):
        """Returns a list containing all the servers we want to iterate over (may be empty).

* my_items : None, string or list which represents all the server ids we want to iterate over"""

        try:
            if (my_items is not None):
                if type(my_items) == types.StringType and my_items.strip() != '':
                    server = self._findServerById(my_items.strip())
                    if server is None:
                        return []
                    else:
                        return [server]

                if type(my_items) == types.ListType and len(my_items) > 0:
                    my_list = []
                    for i in my_items:
                        server = self._findServerById(my_items.strip())
                        if server is not None:
                            my_list.append(server)

                        return my_list
        except:
            pass

        liste = []
        for DA in self.objectValues([utils.EXISTDA_METATYPE]):
            try:
                if self.restrictedTraverse(DA.id) != None:
                    liste.append(DA)
            except:
                pass

        return liste





    ###############################################################################
    ### XMLRPC & eXist methods


    security.declareProtected(utils.PERM_READ_ACCESS, 'getId')
    def getId(self):
        """Returns the id of the object"""
        return self.id

    security.declareProtected(utils.PERM_READ_ACCESS, 'getTitle')
    def getTitle(self):
        """Returns the title of the object"""
        return self.title

    security.declareProtected(utils.PERM_READ_ACCESS, 'getEncoding')
    def getEncoding(self):
        """Returns the encoding of the object"""
        return self.encoding


    security.declareProtected(utils.PERM_READ_ACCESS, 'listDAids')
    def listDAids(self):
        """Returns a list of the ids of the DA contained in the syndicator."""
        liste = []
        for DA in self._getIteratedServers(None):
            liste.append(DA.id)

        return liste

    security.declareProtected(utils.PERM_READ_ACCESS, 'listDAs')
    def listDAs(self):
        """Returns a list of DAs contained in the syndicator."""
        liste = []
        for DA in self._getIteratedServers(None):
            liste.append(DA)

        return liste


    security.declareProtected(utils.PERM_MANAGE_ACCESS, 'isOnline')
    def isOnline(self,servers=None):
        """Gets running servers.

* Returns a list containing tuples (id of servers, 1 if online | 0 otherwise)."""

        liste_online = []

        for DA in self.objectValues([utils.EXISTDA_METATYPE]):
            liste_online.append(DA.isOnline())

        return liste_online


    security.declareProtected(utils.PERM_READ_ACCESS, 'getFilesFromQuery')
    def getFilesFromQuery(self, query, **kws):
        """Query all the DBs in the syndicator.

* Returns a list of tuples like this (eXistDA object, filename) where filename matches the query

* 'query' : a string containing an XPATH query or an XQuery

* '**kws' : see eXistDA for doc. Ignored for the moment, we'll see later how to do this."""

        liste = []
        ns = {}
        if kws.has_key(utils.OK_NAMESPACES):
            ns = kws[utils.OK_NAMESPACES]

        for DA in self.objectValues([utils.EXISTDA_METATYPE]):
            try:
                if kws.has_key(utils.KEY_VARIABLES):
                    for file in DA.getFilesFromQuery(query, object_only=1, variables=kws[utils.KEY_VARIABLES], namespaces=ns):
                        liste.append((DA, file))
                else:
                    for file in DA.getFilesFromQuery(query, object_only=1, namespaces=ns):
                        liste.append((DA, file))
            except:
                pass

        liste_def = []
        for res_A in liste[:-1]:
            suppr = False
            for res_B in liste[liste.index(res_A)+1:]:
                if res_A[0].server == res_B[0].server:
                    if len(res_A[1]) < len(res_B[1]):
                        suppr = True
            if suppr != True:
                liste_def.append(res_A)

        return liste_def


    security.declareProtected(utils.PERM_READ_ACCESS, 'query')
    def query(self, query, xmled=1, **kws):
        """Query all the DBs in the syndicator.

* Returns a 'eXistDAresultsSet' object containing the results for all DAs returned by the queries.

* 'query' : a string containing an XPATH query or an XQuery

* 'xmled' : 1 to return a valid xml string (with <?xml... declaration), 0 to return the result as it comes from eXist

* 'kws' : other parameters

  * 'verbose' : if set to 1, returns a list of lists '[[DA1,[res1, nb_hist_1, query_time_1]], [DA2,[res2, nb_hits_2, query_time_2], ...]]'

  * 'variables' : dict containing variables to pass to the xquery
  """

        if utils.DEBUG >= 3:
            LOG("eXistDAsyn.py - query :", DEBUG, "Entering query method")

        resSet = eXistDAresult.eXistDAresultsSet(encoding = self.encoding)

        ns = {}
        if kws.has_key(utils.OK_NAMESPACES):
            ns = kws[utils.OK_NAMESPACES]

        old_DAs = []
        for DA in self.objectValues([utils.EXISTDA_METATYPE]):
            if utils.DEBUG >= 2:
                LOG("eXistDAsyn.py - query :", DEBUG, "Querying %s" % DA.server)
            #try:
            DA_prot = self.restrictedTraverse(DA.id)
            if utils.DEBUG >= 2:
                LOG("eXistDAsyn.py - query :", DEBUG, "DA_prot for this DA is %s" % str(DA_prot))
            if not(DA_prot.server in old_DAs) and DA_prot != None:
                if kws.has_key(utils.KEY_VARIABLES):
                    thisDA_resSet = DA_prot.query(query, variables=kws[utils.KEY_VARIABLES], namespaces=ns)
                else:
                    thisDA_resSet = DA_prot.query(query, namespaces=ns)


                LOG("eXistDAsyn.py - query :", DEBUG, "resSet is %s" % str(resSet))
                LOG("eXistDAsyn.py - query :", DEBUG, "thisDA_resSet is %s" % str(thisDA_resSet))
                if thisDA_resSet is not None:
                    if resSet is not None:
                        resSet = resSet + thisDA_resSet
                    else:
                        resSet = thisDA_resSet


                if utils.DEBUG >= 3:
                    LOG("eXistDAsyn.py - query :", DEBUG, "Adding query result from %s to syndicator resultsSet")
                    LOG("eXistDAsyn.py - query :", DEBUG, "My new resultsSet is : %s " % resSet.getMergedXML())

                old_DAs.append(DA_prot.server)
            #except:
                #pass

        return resSet



    security.declareProtected(utils.PERM_READ_ACCESS, 'getDoc')
    def getDoc(self, doc_name, xsl='', pretty_print=utils.DEFAULT_PP, **kws):
        """Retrieve a document in one of our DBs.

* Returns a string containing the (XSL transformed if suited) XML document.

* 'doc_name' : a string containing the server, the full path and name of an existing document in a DB

* 'xsl' : a string containing the full path and name of an existing XSL document in the DB (same as doc for the moment). If an empty string is passed, no XSLT is done

* 'if pretty_print' == 1, then the returned string is "pretty printed", ie indented. Else, the string is returned as it is saved in the DB"""

        DA = self._findServerByURI(doc_name)
        if DA is not None:

            if kws.has_key(utils.DICT_STYLESHEET_PARAM):
                return utils.convert(DA.getDoc(doc_name, xsl, pretty_print, stylesheet_param=kws[utils.DICT_STYLESHEET_PARAM]), DA.encoding, self.encoding)

            else:
                return utils.convert(DA.getDoc(doc_name, xsl, pretty_print), DA.encoding, self.encoding)



        return ""


    security.declareProtected( utils.PERM_WRITE_ACCESS, 'xupdate' )
    def xupdate(self, res_name, xupdate_doc):
        """Issue a xupdate command to update a document or a whole collection in the database. If 'res_name' is an eXist URI, only this database (if it's in the syndicator) will be "XUpdated". If no server name is given, the command is issued on all DA in the syndicator.

* Returns the number of server where documents have been modified or raise an exception if pb

* 'res_name' : the name (with complete path) of a collection or a document

* 'xupdate_doc' : a string containing a xupdate file
       """
        nb_servers = 0

        if iseXistURI(res_name) :
            DA = self._findServerByURI(res_name)
            if DA is not None:
                DA.xupdate(utils.getRscNameFromURI(res_name), utils.convert(xupdate_doc, self.encoding, DA.encoding))
                nb_servers = nb_servers + 1
        else:
            for DA in self.objectValues([utils.EXISTDA_METATYPE]):
                try:
                    DA.xupdate(res_name, utils.convert(xupdate_doc, self.encoding, DA.encoding))
                    nb_servers = nb_servers + 1
                except:
                    pass

        return nb_servers

    security.declareProtected( utils.PERM_READ_ACCESS, 'listColl' )
    def listColl(self, base_coll=utils.EXIST_ROOT_COLL, recursive=0, full_path=1):
        """Lists collections in one DA (if server name is passed) or all DA applicable.

'base_coll' : URI of an eXist server (full or not)

'recursive' : integer, 1 will look into all subcollections, 0 only in the collection passed

'full_path' : integer, 1 will print full_path, 0 not
"""

        liste = []
        for DA in self.objectValues([utils.EXISTDA_METATYPE]):
            try:
                liste.append((DA.id,DA.listColl(base_coll, recursive, full_path)))
            except:
                pass

        return liste


    ## End XMLRPC & eXist methods
    ##########################################################################################

    security.declareProtected( utils.PERM_MANAGE_ACCESS, 'manage_edit' )
    def manage_edit(self, title="", encoding=utils.DEFAULT_ENCODING, REQUEST=None):
        """Change values of parameters"""
        # Avoid empty encoding
        if encoding.strip() == '':
            encoding = utils.DEFAULT_ENCODING

        self.title = str(title)
        self.encoding = str(encoding)

        if REQUEST is not None:
            return MessageDialog(
              title = 'Edited',
              message = "Properties for %s changed." % self.id,
              action = './manage_main',
            )

InitializeClass(eXistDAsyn)
