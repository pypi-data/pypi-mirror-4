# -*- coding: iso-8859-15 -*-
#################################################################################
#										#
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,		#
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez    		#
# Christian Martel								#
#										#
# This program is free software; you can redistribute it and/or			#
# modify it under the terms of the GNU General Public License			#
# as published by the Free Software Foundation; either version 2		#
# of the License, or (at your option) any later version.			#
# This program is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
# GNU General Public License for more details.                                  #
#                                                                               #
# You should have received a copy of the GNU General Public License             #
# along with this program; if not, write to the Free Software      		#
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.   #
#										#
#################################################################################

__doc__ = """ Zope OAI Namespace """

import urllib
import Globals
from Globals import HTMLFile
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
import App
from pyOAIMH.OAINamespace import OAINamespace

import DateTime, random

import zOAISupport  # for processId

oai_dc_defaults = {
    'schema':'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
    'prefix':'oai_dc',
    'description':'Open Archives Initiative metadata format based on Dublin Core',
    'namespace':'http://www.openarchives.org/OAI/2.0/oai_dc/',
    'shortname':'OAI Dublin Core',
    'rootNode':'dc',
    'possibleRootNode':['dc:dc', 'dc:dublinCore', 'dc:dublincore'],
    'idPath':'*:identifier',
    'nsDeclaration':['dc="http://purl.org/dc/elements/1.1/"'],
    'nsMainDeclaration':'',
    }

oai_lom_defaults = {
    'schema':'http://www.rdn.ac.uk/oai/lom/20040413/lom.xsd',
    'prefix':'lom',
    'description':'Open Archives Initiative metadata format based on LOM',
    'namespace':'http://ltsc.ieee.org/xsd/LOM',
    'shortname':'OAI LOM',
    'rootNode':'lom',
    'possibleRootNode':['lom:lom'],
    'idPath':'*:technical/*:location',
    'nsDeclaration':['lom="http://ltsc.ieee.org/xsd/LOM"', 'lomfr="http://www.lom-fr.fr/xsd/LOMFR"'],
    'nsMainDeclaration':'',
    }

oai_cdm_defaults = {
    'schema':'http://cdm.nou.no/CDM.xsd',
    'prefix':'oai_cdm',
    'description':'Open Archives Initiative metadata format based on CDM',
    'namespace':'http://www.pentila.com/produits/ZOpenArchives/oai_cdm',
    'shortname':'OAI CDM',
    'rootNode':'CDM',
    'possibleRootNode':['CDM'],
    'idPath':'orgUnit/orgUnitID',
    'nsDeclaration':['cdm="http://www.pentila.com/produits/ZOpenArchives/oai_cdm"'],
    'nsMainDeclaration':'',
    }


manage_addOAIExistNamespaceForm = HTMLFile('dtml/manage_addOAIExistNamespaceForm', globals())

def manage_addOAIExistNamespace(self, ns_prefix=None,
                                ns_rootNode=None,
                                ns_possibleRootNode=[],
                                ns_idPath=None,
                                ns_nsDeclaration=[],
                                ns_nsMainDeclaration=None,
                                ns_description=None,
                                ns_shortname=None,
                                ns_schema=None,
                                ns_namespace=None,
                                REQUEST=None):
    """ method for adding a new OAI eXist namespace """

    # print "in manage add OAI Namespace", self

    try:
        id = zOAISupport.processId(ns_prefix)
        OAI_NS = zOAIExistNamespace( id,
                                     ns_prefix,
                                     ns_rootNode,
                                     ns_possibleRootNode,
                                     ns_idPath,
                                     ns_nsDeclaration,
                                     ns_nsMainDeclaration,
                                     ns_description,
                                     ns_shortname,
                                     ns_schema,
                                     ns_namespace)
    except:
        import traceback
        traceback.print_exc()
        RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20un%20titre')
        return None

    self._setObject(id, OAI_NS)
    # get back OAI Record object
    #
    OAI_NS = getattr(self, id)
    OAI_NS.initialize()
    OAI_NS.index_object()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')


class zOAIExistNamespace(OAINamespace,App.Management.Navigation, SimpleItem, Implicit):
    """ """

    meta_type = 'Exist Open Archive Namespace'
    default_document = 'index_html'
    default_catalog = 'OAI_Catalog'
    ns_nsMainDeclaration = ''

    manage_options = (
        {'label': 'Information',
         'action': 'index_html'
         },
         {'label': 'XSL filters',
         'action': 'manage_nameSpaceFilters'
         },
        )

    index_html = HTMLFile("dtml/manage_OAIExistNamespaceUpdateForm",globals())
    manage_nameSpaceFilters = HTMLFile("dtml/manage_OAIExistNamespaceFiltersForm",globals())

    def __init__(self,
                 id,
                 ns_prefix=None,
                 ns_rootNode=None,
                 ns_possibleRootNode=[],
                 ns_idPath=None,
                 ns_nsDeclaration=[],
                 ns_nsMainDeclaration=None,
                 ns_description=None,
                 ns_shortname=None,
                 ns_schema=None,
                 ns_namespace=None):
        """ """

        self.id = id

        try:
            OAINamespace.__init__(self, ns_prefix, ns_description, ns_shortname, ns_schema, ns_namespace)
        except:
            # this is needed for some reason when python
            # version is < 2.2
            OAINamespace.__init__.im_func(self, ns_prefix, ns_description, ns_shortname, ns_schema, ns_namespace)

        self.set_nsRootNode(ns_rootNode)
        self.set_nsPossibleRootNode(ns_possibleRootNode)
        self.set_nsIdPath(ns_idPath)
        self.set_nsNsDeclaration(ns_nsDeclaration)
        self.set_nsMainNsDeclaration(ns_nsMainDeclaration)

        ## list what contains XSLFilters apply to this namespace
        self.xslFilters = []



    def initialize(self):
        """ """
        pass

    def title(self):
        """ """
        return self.get_nsShortname()


    def index_object(self):
        """
        """
        # print "indexing record"
        try:
            getattr(self, self.default_catalog).catalog_object(self, urllib.unquote('/' + self.absolute_url(1) ))
        except:
            pass

    def unindex_object(self):
        """
        """
        try:
            getattr(self, self.default_catalog).uncatalog_object(urllib.unquote('/' + self.absolute_url(1) ))
        except:
            pass

    def reindex_object(self):
        """
        """
        self.unindex_object()
        self.index_object()


    #### rootNode

    def get_nsRootNode(self):
        """ """
        return self.ns_rootNode

    def set_nsRootNode(self, value):
        """ """
        self.ns_rootNode = value


    def get_nsPossibleRootNode(self):
        """ """
        return self.ns_possibleRootNode

    def set_nsPossibleRootNode(self, value):
        """ """
        if type(value) == type(''):
            value = map(lambda x:x.strip(), value.split(','))
        self.ns_possibleRootNode = value

    def get_nsIdPath(self):
        """ """
        return self.ns_idPath

    def set_nsIdPath(self, value):
        """ """
        self.ns_idPath = value

    def get_nsNsDeclaration(self):
        """ """
        return self.ns_nsDeclaration

    def set_nsNsDeclaration(self, value):
        """ """
        self.ns_nsDeclaration = value

    def get_nsMainNsDeclaration(self):
        """ """
        if not hasattr(self, 'ns_nsMainDeclaration'):
            self.ns_nsMainDeclaration = ''
        return self.ns_nsMainDeclaration

    def set_nsMainNsDeclaration(self, value):
        """ """
        self.ns_nsMainDeclaration = value


    def get_nsDictionary(self, REQUEST=None):
        """ """
        nsdict = dict()
        nsdict['description'] = self.ns_description
        nsdict['shortname'] = self.ns_shortname
        nsdict['namespace'] = self.ns_namespace
        nsdict['prefix'] = self.ns_prefix
        nsdict['schema'] = self.ns_schema
        nsdict['rootNode'] = self.ns_rootNode
        nsdict['possibleRootNode'] = self.ns_possibleRootNode
        nsdict['idPath'] = self.ns_idPath
        nsdict['nsDeclaration'] = self.ns_nsDeclaration
        nsdict['mainNsDeclaration'] = self.ns_nsMainDeclaration
        nsdict['XSLFilter4IP'] = self.getXSLFilterName(REQUEST=REQUEST)

        return nsdict

    # manage methods
    #



    def manage_OAIExistNamespaceUpdate(self,
                                       ns_prefix=None,
                                       ns_rootNode=None,
                                       ns_possibleRootNode=[],
                                       ns_idPath=None,
                                       ns_nsDeclaration=[],
                                       ns_mainNsDeclaration=None,
                                       ns_description=None,
                                       ns_shortname=None,
                                       ns_namespace=None,
                                       ns_schema=None,
                                       REQUEST=None,
                                       RESPONSE=None):
        """ """

        self.set_nsPrefix(ns_prefix)
        self.set_nsRootNode(ns_rootNode)
        self.set_nsPossibleRootNode(ns_possibleRootNode)
        self.set_nsIdPath(ns_idPath)
        self.set_nsNsDeclaration(ns_nsDeclaration)
        self.set_nsMainNsDeclaration(ns_mainNsDeclaration)
        self.set_nsDescription(ns_description)
        self.set_nsShortname(ns_shortname)
        self.set_nsSchema(ns_schema)
        self.set_nsNamespace(ns_namespace)

        RESPONSE.redirect(self.absolute_url() + '/index_html?manage_tabs_message=Namespace%20has%20been%20updated')



    def checkNamespace(self):
        """
        FUTURE: want to use this for validating
          namespaces as they are edited and created.
          ideally, would go and collect the validating schema
          and store within namespace object.
        """

        errors = 0
        ns_dict = self.namespaces
        msg = 'manage_tabs_message=No%20message'

        # setup string for return in case of errors
        #   so the user doesn't lose what they have entered
        #
        vars = ''
        for name, value  in [ ('ns_prefix', ns_prefix), ('ns_rootNode', ns_rootNode), ('ns_possibleRootNode', ns_possibleRootNode),
                              ('ns_idPath', ns_idPath), ('ns_nsDeclaration', ns_nsDeclaration),
                              ('ns_schema', ns_schema), ('ns_namespace', ns_namespace),
                              ('ns_shortname', ns_shortname), ('ns_description', ns_description)]:
            vars = vars + '&' + name + '=' + value



        # check to make sure have proper values for inputs

        # NAMESPACE
        if ns_namespace == "" and not errors:
            msg = 'manage_tabs_message=Namespace%20is%20invalid'
            errors = 1

        if ns_dict.has_key(ns_namespace) and not errors:
            errors = 1
            msg = 'manage_tabs_message=Namespace%20already%20exists'

        # SHORTNAME
        if ns_shortname == "" and not errors:
            msg = 'manage_tabs_message=Shortname%20is%20invalid'
            errors = 1

        # DESCRIPTION
        if ns_description == "" and not errors:
            msg = 'manage_tabs_message=Description%20is%20invalid'
            errors = 1

        # PREFIX
        if ns_prefix == "" and not errors:
            msg = 'manage_tabs_message=Prefix%20is%20invalid'
            errors = 1

        # ROOT NODE
        if ns_rootNode == "" and not errors:
            msg = 'manage_tabs_message=RootNode%20is%20invalid'
            errors = 1

        # POSSIBLE ROOT NODE
        if ns_rootNode == "" and not errors:
            msg = 'manage_tabs_message=RootNode%20is%20invalid'
            errors = 1

        # ID PATH
        if ns_idPath == "" and not errors:
            msg = 'manage_tabs_message=IDPath%20is%20invalid'
            errors = 1

        # NS DECLARATION
        if ns_nsDeclaration == "" and not errors:
            msg = 'manage_tabs_message=NS%20decalaration%20is%20invalid'
            errors = 1

        # SCHEMA
##        if ns_schema == "" and not errors:
##            errors = 1
##            msg = 'manage_tabs_message=Schema%20is%20invalid'


        # everything is OK
        if not errors:
            ns_dict[ns_namespace] = { 'prefix':ns_prefix,
                                      'rootNode':ns_rootNode,
                                      'schema':ns_schema,
                                      'namespace':ns_namespace,
                                      'shortname':ns_shortname,
                                      'description':ns_description,
                                      'possibleRootNode':ns_possibleRootNode,
                                      'idPath':ns_idPath,
                                      'nsDeclaration':ns_nsDeclaration,
                                      }

            self.namespaces = ns_dict
            msg = 'manage_tabs_message=Server%20has%20been%20updated'
            vars = ''


            RESPONSE.redirect(self.absolute_url() + '/manage_serverNamespaces?' + msg + vars )

    ###############################################################
    ##
    ##  Methods for XSL filters management and application
    ##
    ###############################################################
    def testIP(self, ip2Test, REQUEST=None):
        """
        return the value corresponding to ip for test purpose
        """
        val = self.getXSLFilterName(IP=ip2Test)
        if not val:
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=no XSLFilter associated')
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=XSLFilter corresponding to %s is %s' % (ip2Test, val))

    def getXSLFilterName(self, IP="", REQUEST=None):
        """
        return the appropriate filter
        """
        if REQUEST==None:
            REQUEST = self.REQUEST
        if IP:
            ipClient = IP
        else:
            ipClient = REQUEST.get('REMOTE_ADDR', '')
        for item in self.getXSLFilters():
            if ipClient.find(item['ipMask']) == 0 or item['ipMask']=='*':
                if item['noXSL']=='1':
                    return ''
                return "xmldb:exist:///db/" + item['xslFilter']
        return ''

    def getXSLFilters(self, active=1):
        """
        return the list of XSLFilters applies on this metadata
        """
        if not hasattr(self, 'xslFilters'):
           self.xslFilters = []
        if active == 0:
           # return the entire list
           return self.xslFilters

        lTMP = []
        for item in self.xslFilters:
           if item['actif'] == '1':
              lTMP.append(item)

        return lTMP

    def editFilters(self, REQUEST=None):
        """
        edit filters from the management interface
        """
        lTMP = []
        lf = self.getXSLFilters(active=0)
        for item in lf:
           key = item['id']
           newFilter = {}
           newFilter['id'] = key
           newFilter['ipMask'] = REQUEST.get(key+'_ipmask', '')
           newFilter['xslFilter'] = REQUEST.get(key+'_xslFilter', '')
           newFilter['actif'] = REQUEST.get(key+'_actif', '0')
           newFilter['noXSL'] = REQUEST.get(key+'_noXSL', '0')
           lTMP.append(newFilter)

        self.xslFilters = lTMP
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=XSLFilter%20saved')

    def delFilters(self, ids=[], REQUEST=None):
        """
        delete filters checked inside the management interface
        """
        lTMP = []
        for item in self.getXSLFilters(active=0):
           if item['id'] not in ids:
              lTMP.append(item)
        self.xslFilters = lTMP
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=XSLFilter%20deleted')

    def addFilterTop(self, new_ipmask="", new_xslFilter="", new_actif="0", new_noXSL="0", REQUEST=None):
        """
        add a new filter at the top of the list
        """
        newFilter = {}
        if new_ipmask:
           newFilter['id'] = str(DateTime.DateTime().millis()) + str(random.randint(1, 10000))
           newFilter['ipMask'] = new_ipmask
           newFilter['xslFilter'] = new_xslFilter
           newFilter['actif'] = new_actif
           newFilter['noXSL'] = new_noXSL
           l = [newFilter]
           self.xslFilters = l + self.getXSLFilters(active=0)
           return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=XSLFilter%20added')
        else:
           return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=You%20must%20edit%20IP%20mask%20field')

    def addFilterBottom(self, new_ipmask="", new_xslFilter="", new_actif="0", new_noXSL="0", REQUEST=None):
        """
        add a new filter at the bottom of the list
        """
        newFilter = {}
        if new_ipmask and new_xslFilter:
           newFilter['id'] = str(DateTime.DateTime().millis()) + str(random.randint(1, 10000))
           newFilter['ipMask'] = new_ipmask
           newFilter['xslFilter'] = new_xslFilter
           newFilter['actif'] = new_actif
           newFilter['noXSL'] = new_noXSL
           self.xslFilters = self.getXSLFilters(active=0) + [newFilter]
           return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=XSLFilter%20added')
        else:
           return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=You%20must%20edit%20all%20fields')


    ## filter position inside the list management
    def moveUp(self, ids=[], REQUEST=None):
        """
        move up the selected filter
        """
        lf = self.getXSLFilters(active=0)
        for id in ids:
           lTMP = []
           i = 0
           for item in lf:
              if item['id'] != id:
                 lTMP.append(item)
                 i += 1
                 if i==len(lf):
                    lf = lTMP
              else:
                 if i == 0:
                    ## first loop
                    break
                 lf = lTMP[:-1] + [item] + [lTMP[-1]] + lf[i+1:]
                 break
        self.xslFilters = lf
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=Filter(s)%20moved%20up')

    def moveDown(self, ids=[], REQUEST=None):
        """
        move down the selected filter
        """
        lf = self.getXSLFilters(active=0)
        ids.reverse()
        for id in ids:
           lTMP = []
           i = 0
           for item in lf:
              if item['id'] != id:
                 lTMP.append(item)
                 i += 1
                 if i==len(lf):
                    lf = lTMP
              else:
                 if i == len(lf)-1:
                    ## first loop
                    break
                 lf = lTMP + [lf[i+1]] + [item] + lf[i+2:]
                 break
        self.xslFilters = lf
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_nameSpaceFilters?manage_tabs_message=Filter(s)%20moved%20down')


