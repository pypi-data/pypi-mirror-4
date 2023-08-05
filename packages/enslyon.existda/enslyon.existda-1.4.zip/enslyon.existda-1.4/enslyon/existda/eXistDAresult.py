"""eXistDAresult.py : a result for eXistDA queries, getDoc or whatever implies XML"""

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


__doc__ = """Results for eXistDA Product"""

import utils
import eXistDA

from types import StringType
from zLOG import LOG, INFO, DEBUG

# Constants
SCRIPT= 'EXISTDARESULT'
cDA   = 'DA'
cXML  = 'xml'
cHITS = 'hits'
cRES  = 'results'
cENC  = 'encoding'
cDOCB = 'docbase'
resACCEPT = [cDA, cXML, cHITS, cENC, cDOCB]
resSetACCEPT = [cRES, cENC]


class eXistDAresult:
    """A result object for eXistDA product. It contains XML and other infos"""

    def __init__(self, DA=None, xml='', docbase='', hits=-1, encoding=utils.DEFAULT_ENCODING):
        """Initialization of the class"""
        if DA != None:
            self.DA = DA
        else:
            raise utils.EXC_MUST_HAVE_A_DA

        self.xml = str(xml)
        self.hits = int(hits)
        self.docbase = "" #docbase
        self.encoding = encoding


    def __setattr__(self, name, value):
        """Attributes setting"""

        if name in resACCEPT:
            if name == cHITS:
                self.__dict__[name] = int(value)
            elif name == cDOCB:
                self.__dict__[name] = '' #value
            elif name == cENC:
                if self.__dict__.has_key(cXML) and self.__dict__.has_key(cENC):
                    self.xml = utils.convert(self.xml, self.encoding, value)
                self.__dict__[name]=value
            else:
                self.__dict__[name] = str(value)


    def __getattr__(self, name):
        """Attributes recovering"""
        if self.__dict__.has_key(name):
            if name == cXML:
                return str(self.__dict__[name])

            return self.__dict__[name]
        else:
            return None


    def __eq__(self, other):
        """Equality comparison"""
        if unicode(self.xml, self.encoding) == unicode(other.xml, other.encoding):
            return True

        return False


    def __neq__(self, other):
        """Not equality"""
        if (unicode(self.xml, self.encoding) == unicode(other.xml, other.encoding)) :
            return False

        return True


    def __add__(self, other):
        """Adds two results and returns a resultSet"""
        if isinstance(other, eXistDAresult):
            return eXistDAresultsSet(self, other)
        else:
            raise TypeError, 'Right operand must be a eXistDAresult'


    def __cmp__(self, other):
        """Comparison. By default, we test hits"""
        return cmp(self.hits, other.hits)


    def __str__(self):
        """String representation"""
        return str(self.xml)
    __repr__ = __str__

    def getDict(self):
        """Returns the dictionary representing the XML result"""

        return utils.getDict(self.xml, encoding=self.encoding)



class eXistDAresultsSet:
    """A results set"""

    def __init__(self, encoding=utils.DEFAULT_ENCODING):
        """Creates an instance from the class, with n DAresults passed in the creation"""
        self.encoding = encoding
        self.__dict__[cRES] = []


    def __getattr__(self, name):
        """Attributes recovering"""
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            return None


    def __getitem__(self, index):
        """ """
        return self.results.__getitem__(index)


    def __setattr__(self, name, value):
        """Attributes setting"""
        if name in resSetACCEPT:
            if name == cRES:
                if self.__dict__.has_key(cENC):
                    self.__dict__[name] = [unicode(str(value)).encode(self.encoding)]
                else:
                    self.__dict__[name] = str(value)
            elif name == cENC:
                new_results = []
                if self.__dict__.has_key(cRES):
                    for result in self.__dict__[cRES]:
                        result.encoding = value # Converts result to a new encoding 'value'
                        new_results.append(result)
                    self.__dict__[cRES] = new_results
                    if utils.DEBUG > 2 :
                        LOG(SCRIPT, DEBUG, "New results for eXistDAResultsSet is : %s" % str(self.results))

                self.__dict__[name] = value


    def __str__(self):
        """String representation"""
        retour =""
        for r in self.results:
            retour = retour + str(r) + '\n'

        return retour
    __repr__ = __str__

    def __add__(self, other):
        """Adds two resultsSets. The encoding is the left operand's one"""
        if isinstance(other, eXistDAresultsSet):
            for result in other.results:
                result.encoding = self.encoding
                self.results += result
            return self
        else:
            raise TypeError, 'Right operand must be a eXistDAresultsSet'


    def __nonzero__(self):
        """Test the 0 value of the class"""
        if len(self.results) == 0:
            return False
        return True


    def __len__(self):
        """Number of items in the list"""
        return len(self.results)


    def count(self, x) :
        """Return the number of occurence of x in the resultsSet. x can be an eXistDAresult, an eXistDA object or an XML string"""
        if isinstance(x, eXistDA.eXistDA):
            listeDA = []
            for result in self.results:
                listeDA.append(result.DA)
            return listeDA.count(x)
        elif isinstance(x, eXistDAresult):
            return self.results.count(x)
        elif type(x) == StringType:
            listeXML = []
            for result in self.results:
                listeXML.append(result.xml)
            return listeXML.count(x)
        else:
            raise TypeError, 'Seeked object must be an eXistDAresult instance, an eXistDA instance, or an XML string'


    def append(self, other):
        """Appends a result to this resultsSet"""

        if isinstance(other, eXistDAresult):
            self.results.append(other)
        else:
            raise TypeError, 'Appended object must be a eXistDAresult'


    def remove(self, x):
        """Removes the first occurence of the result containing x in the list. x can be an eXistDAresult, an eXistDA object, or an XML string"""
        if isinstance(x, eXistDA.eXistDA):
            for result in self.results:
                if x == result.DA:
                    self.results.remove(result)
                    break
        elif isinstance(x, eXistDAresult):
            self.results.remove(x)
        elif type(x) == StringType:
            for result in self.results:
                if x == result.xml:
                    self.results.remove(result)
                    break
        else:
            raise TypeError, 'Removed object must be an eXistDAresult instance, an eXistDA instance, or an XML string'


    def index(self, x):
        """Returns the index of the first occurence of x in the _results list.  x can be an eXistDAresult, an eXistDA object, or an XML string"""
        if isinstance(x, eXistDA.eXistDA):
            for result in self.results:
                if x == result.DA:
                    return self.results.index(result)
        elif isinstance(x, eXistDAresult):
            return self.results.index(x)
        elif type(x) == StringType:
            for result in self.results:
                if x == result.xml:
                    return self.results.index(result)
        else:
            raise TypeError, 'Seeked object must be an eXistDAresult instance, an eXistDA instance, or an XML string'


    def sort(self, fn=None):
        """Sorts the _results by score. Use reverse to reverse the order"""
        if not (fn is None):
            self.results.sort(fn)
        else:
            self.results.sort()


    def reverse(self):
        """Reverse the order of the results list"""
        self.results.reverse()


    def getMergedXML(self, xmled=True):
        """Returns the result as a big simple XML file"""
        str_res = ''
        if xmled:
            str_res = '<?xml version="1.0" encoding="%s"?><results>' % self.encoding

        for res in self.results:
            str_res += "<result>%s</result>" % res.xml

        if xmled:
            str_res += "</results>"

        return str_res


    def listResultsDocs(self):
        """Returns a list containing the URIs of each doc verifying the query

**BROKEN** : always returns the name of the server and its port, but not the path to the file
        """

        lst_res = []
        for res in self.results:
            str_res = utils.HEADER_EXIST_URI + res.DA.server + ':' + res.DA.port + res.docbase
            lst_res.append(str_res)

        return lst_res


    def getDict(self):
        """Returns a list of dictionaries representing the xml resultsSet"""

        res_list = []
        for elem in self.results:
            res_list.append(elem.getDict())

        return res_list


    def getMergedDict(self, xmled=True):
        """Returns a dictionary of the merged version of the resultsSet"""

        return utils.getDict(self.getMergedXML(xmled), self.encoding)

