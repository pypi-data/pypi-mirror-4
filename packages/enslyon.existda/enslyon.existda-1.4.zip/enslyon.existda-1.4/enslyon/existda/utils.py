"""utils.py : Utilities for eXistDA Product"""
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


__doc__ = """Utilities for eXistDA Product"""

import types, urllib
from App.Dialogs import MessageDialog
import xml.dom.minidom
import htmlentitydefs
from zLOG import LOG, INFO

# Changeable constants
USE_CDOMLETTE       = True                               # If set to True, xslt.py will use 4Suite cDomlette instead of Domlette to make transformations.
USE_EXPAT           = True                               # Use expat to compute dictionnaries if available
USE_XSLTPROC        = True                               # Use XSLTPROC if available in place of 4Suite
XSLTPROC            = "xsltproc"                         # Executable for xsltproc, with full path if needed


# Global constants for eXistDA and syndicator
DEBUG               = 0                                  # Set to 1,2,3 to have debug messages on the console (or log) (3 is the most verbose), or 0 to disable
THIS_SCRIPT         = "EXISTDA.utils.py"                 # Name of this script
CODE_ENCODING       = 'UTF-8'                            # Format in which the code itself is encoded
OBJ_ONLY            = 'object_only'                      # dict key for eXistDA._getAnythingAsString object_only parameter
VERBOSE             = 'verbose'                          # dict key for query
XSLT_TIMEOUT        = 20                                 # Timeout in secs for xsltproc


# Dict keys for extra parameters
DICT_STYLESHEET_PARAM    = "stylesheet_param"
DICT_STYLESHEET_BASE_URI = "xsl_base_uri"

# Zope constants
EXISTDA_METATYPE    = "eXist Database Adapter"           # Metatype of the database adapter
EXISTDASYN_METATYPE = "eXist DB syndicator"              # Metatype of the syndicator
EXISTMETHOD_METATYPE= "eXist Method"                     # Metatype of an xquery method
EXISTDACACHEMANAGER_METATYPE = "eXistDA Cache Manager"   # Metatype of a cache manager
REXISTDA_METATYPE   = "eXist Remote Database Adapter"    # Metatype of the remote database adapter

# Cache manager types
RAMCACHE            = "RAM Cache Manager"                # Cache manager in RAM
ZODBCACHE           = "ZODB Cache Manager"               # Cache manager within the ZODB
FSCACHE             = "FileSystem Cache Manager"         # Cache manager on the file system
ALL_CACHE_TYPES = [RAMCACHE, ZODBCACHE, FSCACHE]         # Don' forget to add any cache manager you need in this list

# Defaults
DEFAULT_PP          = 1                                  # Default for pretty print (0 or 1)
EXIST_ROOT_COLL     = '/db'                              # Root collection of the DB (usually '/db') !!!! NO ENDING / !!!!
DEFAULT_ENCODING    = 'UTF-8'                            # Default encoding if nothing is passed during init or mod
DEFAULT_PORT        = '8080'                             # Default eXist XMLRPC server's port if nothing is passed during init or mod
DEFAULT_CACHEMANAGER_TYPE = RAMCACHE                     # Default cache manager type
DEFAULT_CACHE_MAXSIZE = 10                               # Default cache max size (in MB)
DEFAULT_XMLRPC_PATH = '/xmlrpc'                          # Default address of eXist embedded XMLRPC server
DEFAULT_ZOPE_XMLRPC_PATH = '/existda'                    # Default address of an eXistDA on a remote Zope server


# Headers for URIs
HEADER_HTTP_URI     = "http://"                          # Beginning of an HTTP URI (usually 'http://')
HEADER_EXIST_URI    = "xmldb:exist://"                   # Beginning of an eXist URI (usually 'xmldb:exist://')
HEADER_FILE_URI     = "file://"                          # Beginning of a file URI (usually 'file://')

# Parameters for XML options
OK_STYLESHEET       = "stylesheet"                       # key of the dict containing the XSL string which renders a doc
OK_INDENT_SPACES    = "indent-spaces"                    # key of the dict containing the space preservation value
OK_ENCODING         = "encoding"                         # key of the dict containing the encoding value
OK_INDENT           = "indent"                           # key of the dict containing the indentation presentation value
OK_STYLESHEET_PARAM = "stylesheet-param"                 # key of the dict containing the XSL parameters
OK_NAMESPACES       = "namespaces"                       # key of the dict containing the namespaces used by an XPath query

KEY_VARIABLES       = "variables"                        # key of the dict used to pass variables to xqueries

# Permissions
PERM_WRITE_ACCESS   = "Write to XMLDB"                   # permission used to have a write access to the DB
PERM_READ_ACCESS    = "View"                             # permission used to have a read access to the DB
PERM_MANAGE_ACCESS  = "View management screens"          # permission used to have a management rights to the DB

# Exceptions throwned by the objects
EXC_DOC_MUST_BE_ON_EXIST_SERVER = "The document must be on eXist, so you must give an eXist URI !"
EXC_CANT_SAVE                   = "The document can't be saved."
EXC_NOT_RESOURCE                = "The given path is not a resource of the DB."
EXC_NOT_STRING                  = "The object can't be returned as a string."
EXC_NOT_THIS_DB                 = "The URI passed is not an URI which represents this object !"
EXC_NO_4SUITE                   = "Can't find 4Suite in your python/lib. External XSLT won't be available"
EXC_MUST_HAVE_A_DA              = "The result must have an eXist DA."
EXC_NOT_DIR                     = "The given path is not a directory on the filesystem."
EXC_NOT_CACHE_TYPE              = "This cache type doesn't exist."



def hasExpat():
    """Returns True if Expat module is available"""
    try:
        import xml.parsers.expat
        return True
    except:
        return False

def hasXSLTProc():
    """Returns True is xsltproc is installed and in the path"""
    try:
        from os import popen
        if popen(XSLTPROC) != None:
            return True
        else:
            return False
    except:
        return False


def isHTTPURI(URI):
    """Verifies if 'URI' is an HTTP URI (ie beggining with 'HEADER_HTTP_URI').

* Returns 1 if 'URI' is an HTTP-like URI. 0 otherwise

* 'URI' : the string to test"""

    try:
        if type(URI) != types.StringType:
            return 0
    except:
        pass

    try:
        if URI[:len(HEADER_HTTP_URI)] == HEADER_HTTP_URI:
            return 1
    except:
        pass

    return 0


def iseXistURI(URI):
    """Verifies if 'URI' is an eXist URI (ie beggining with HEADER_EXIST_URI).

* Returns 1 if 'URI' is an eXist-like URI. 0 otherwise

* 'URI' : the string to test"""

    try:
        if type(URI) != types.StringType:
            return 0
    except:
        pass

    try:
        if URI[:len(HEADER_EXIST_URI)] == HEADER_EXIST_URI:
            return 1
    except:
        pass

    return 0

def isFileURI(URI):
    """Verifies if 'URI' is a file URI (ie beggining with HEADER_FILE_URI).

* returns 1 if 'URI' is a file-like URI. 0 otherwise

* 'URI' : the string to test"""

    try:
        if type(URI) != types.StringType:
            return 0
    except:
        pass

    try:
        if URI[:len(HEADER_FILE_URI)] == HEADER_FILE_URI:
            return 1
    except:
        pass

    return 0

def is4SuiteAvailable():
    """Returns 1 if 4Suite can be used to make external XSLT, 0 otherwise."""
    try:
        from Ft.Xml.Xslt import Processor
        from Ft.Xml.InputSource import DefaultFactory
        return 1 # True
    except:
        return 0 # False


def URIHasServerName(URI):
    """Returns True if the URI is containing a server name, False otherwise.

* 'URI' : a string containing the URI to scan."""

    if URI[:len(HEADER_EXIST_URI)+1] == HEADER_EXIST_URI + '/':
        return 0

    elif URI[:len(HEADER_HTTP_URI)+1] == HEADER_HTTP_URI + '/':
        return 0

    return 1


def getServerNameFromURI(URI):
    """Get the server name from an URI.

* Returns a string containing the name of the [eXist | HTTP] server corresponding to the URI (with the port number). Returns empty string if none."""

    if iseXistURI(URI) or isHTTPURI(URI):
        try:
            if URIHasServerName(URI.strip()):
                return URI.strip().split('//')[1].split('/',1)[0]
            else:
                return ""
        except:
            return ""

    return ""


def getRscNameFromURI(URI):
    """Get the resource name from an URI.

* Returns the name of the [eXist | HTTP] resource corresponding to the URI. Returns empty string if none."""

    if iseXistURI(URI) or isHTTPURI(URI):
        try:
            if URIHasServerName(URI.strip()):
                return "/" + URI.strip().split('//')[1].split('/',1)[1]
            else:
                return "/" + URI.strip().split('///')[1]
        except:
            return ""

    return ""


def convert(text, encoding_from, encoding_to):
    """Converts 'text' , encoded in 'encoding_from' to the encoding 'encoding_to'.

* returns the text converted into 'encoding_to' (if necessary) or raise an exception if something weird happened

* 'text' : a string containing the text to convert

* 'encoding_from' : a string containing the encoding of the text to convert

* 'encoding_to' : a string containing the encoding to convert the text to"""

    if encoding_from.lower().strip() != encoding_to.lower().strip():
        return unicode(text, encoding_from).encode(encoding_to)

    return text


def getInvalidMsg(server='', port='', username='', password='', encoding=''):
    """Verifies if the parameters passed to create or modify an eXistDA object are valid for use. Not all is verified...

* Returns 'None' if no error is found. Returns a MessageDialog object if something bad happened."""

    # We can't permit localhost or 127.0.0.1 for server address because of syndication
    # which needs to return the full qualified server name.
    if str(server).strip() == "ocalhost" or str(server).strip() == "127.0.0.":
        return MessageDialog(
            title = 'Error',
            message = "Server name can't be %s, it must be the full qualified name of the server. Changes not saved." % str(server).strip(),
            action = './manage_main')

    # Server name can't be empty
    if str(server).strip() == "":
        return MessageDialog(
            title = 'Error',
            message = "Server name can't be empty.",
            action = './manage_main')

    # Port must be an integer between 1 and 65535
    try:
        if int(str(port).strip()) < 1 or int(str(port).strip()) > 65535:
            # Not a port number...
            raise ValueError

    except ValueError:
        return MessageDialog(
            title = 'Error',
            message = "Port number must be an integer between 1 and 65535.",
            action = './manage_main')

    return None

# Utilities to get the DOM of an XML document into a python dictonary

def recurse_getDict(noeud, encoding, lst_nom_noeuds, cedico):
    """Returns a part of a dict which keys are XML tags and their values."""
    cle = '/'.join(lst_nom_noeuds).encode(encoding)

    for sousnoeud in noeud.childNodes:
        if sousnoeud.nodeType == sousnoeud.TEXT_NODE:
            valeur = sousnoeud.data.encode(encoding).strip().replace('\n','')
            if valeur != '':
                if cedico.has_key(cle):
                    cedico[cle].append(valeur)
                else:
                    cedico.update({cle:[valeur]})
        else:
            lst_nvl_cle = lst_nom_noeuds + [sousnoeud.tagName.encode(encoding)]
            cedico = recurse_getDict(sousnoeud, encoding, lst_nvl_cle, cedico)

    return cedico


def getDict(fichier_string, encoding=DEFAULT_ENCODING):
    """Returns the dict by calling the recursive method recurse_getDict."""

    for i in htmlentitydefs.entitydefs:
        if fichier_string.find("&%s;" % i) != -1 and i != 'amp':
            # We don't replace &amp; because & is not supported by expat.
            fichier_string = fichier_string.replace("&%s;" % i, htmlentitydefs.entitydefs[i])

    try:
        # Try to use expat if available and asked by user
        if USE_EXPAT and hasExpat():
            import xml.parsers.expat
            d = XMLToDict(encoding)
            return d.parseXML(fichier_string)
        else:
            doc = xml.dom.minidom.parseString(fichier_string)
            return recurse_getDict(doc.documentElement, encoding, [doc.documentElement.tagName.encode(encoding)], {})
    except:
        doc = xml.dom.minidom.parseString(fichier_string)
        return recurse_getDict(doc.documentElement, encoding, [doc.documentElement.tagName.encode(encoding)], {})


def mergeDict(dict1, dict2):
    """Returns a new dictionary by merging 'dict1' and 'dict2'.

**WARNING** : the two dicts must have the same structure ! If 'dict1["my_key"] and 'dict2["my_key"]' exist and don't have the same type of value,
an error will be raised."""

    dict = dict1.copy

    for one_key in dict2.keys():
        if dict.has_key(one_key):
            dict[one_key] = dict[one_key] + dict2[one_key]
        else:
            dict[one_key] = dict2[one_key]

    return dict

class XMLToDict:
    """Class implementing expat parser to map an XML string to a python dictionary"""

    def _start_element(self, name, attrs):
        """What to do when processing an opening tag"""
        self.tags_stack.append(name)
        for k in attrs.keys():
            key = '/'.join(self.tags_stack).encode(self.encoding) + '/@' + k.encode(self.encoding)
            if self.xml_dict.has_key(key):
                if self.wrote_data[key]:
                    self.xml_dict[key][-1] += attrs[k].encode(self.encoding)
                else:
                    self.xml_dict[key].append(attrs[k].encode(self.encoding))
            else:
                self.xml_dict[key] = [attrs[k].encode(self.encoding)]
            self.wrote_data[key] = True

    def _end_element(self, name):
        """What to do when processing a closing tag"""
        key = '/'.join(self.tags_stack).encode(self.encoding)
        self.tags_stack.pop()
        self.wrote_data[key] = False

    def _char_data(self, data):
        """What to do when processing character data in a tag"""
        key = '/'.join(self.tags_stack).encode(self.encoding)
        if data.strip().replace('\n', '') != '':
            if self.xml_dict.has_key(key):
                if self.wrote_data[key]:
                    self.xml_dict[key][-1] += data.encode(self.encoding)
                else:
                    self.xml_dict[key].append(data.encode(self.encoding))
            else:
                self.xml_dict[key] = [data.encode(self.encoding)]
            self.wrote_data[key] = True


    def __init__(self, encoding=DEFAULT_ENCODING):
        """Construction of the class, with encoding awareness"""
        self.encoding = str(encoding)
        self.xml_dict = {}
        self.tags_stack = []
        self.attrs_dict = {}
        self.wrote_data = {}


    def parseXML(self, xml_string):
        """Parse 'xml_string' and returns a dictionary mapped on the XML DOM"""
        p = xml.parsers.expat.ParserCreate(self.encoding)

        p.StartElementHandler = self._start_element
        p.EndElementHandler   = self._end_element
        p.CharacterDataHandler= self._char_data
        p.buffer_text = True

        if (len(xml_string) > 0):
            p.Parse(xml_string)

        return self.xml_dict


# Message LOG at startup
if hasExpat():
    if USE_EXPAT:
        LOG(THIS_SCRIPT, INFO, "Expat is available and will be used. If you want to use minidom instead, please change USE_EXPAT to False in %s." % THIS_SCRIPT)
    else:
        LOG(THIS_SCRIPT, INFO, "Expat is available but won't be used. If you want to use expat, please change USE_EXPAT to True in %s." % THIS_SCRIPT)
else:
    LOG(THIS_SCRIPT, INFO, "Expat is **NOT** available. minidom will be used instead. Please install pyexpat (see http://pyxml.sourceforge.net) if you want to use it.")

if hasXSLTProc():
    if USE_XSLTPROC:
        LOG(THIS_SCRIPT, INFO, "xsltproc is available, and will be used. If you don't want to use xsltproc but 4Suite, please change USE_XSLTPROC to False in %s." % THIS_SCRIPT)
    else:
        LOG(THIS_SCRIPT, INFO, "xsltproc is available, but won't be used. If you want to use xsltproc and not 4Suite, please change USE_XSLTPROC to True in %s." % THIS_SCRIPT)
else:
    LOG(THIS_SCRIPT, INFO, "xsltproc is **NOT** available (xsltproc not installed or not in path). 4Suite will be used if found. Else, external XSLT won't be available for eXistDA.")

# End message LOG
