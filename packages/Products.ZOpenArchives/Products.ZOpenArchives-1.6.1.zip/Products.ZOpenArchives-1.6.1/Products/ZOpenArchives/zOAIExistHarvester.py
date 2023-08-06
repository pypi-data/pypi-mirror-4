# -*- coding: iso-8859-15 -*-
#################################################################################
#                                       #
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,      #
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez         #
# Christian Martel                              #
#                                       #
# This program is free software; you can redistribute it and/or         #
# modify it under the terms of the GNU General Public License           #
# as published by the Free Software Foundation; either version 2        #
# of the License, or (at your option) any later version.            #
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

__doc__ = """Zope Exist OAI Site Harvester"""

import string

from Globals import HTMLFile, Persistent
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
import App
import zOAIRecord # for manage_addOAIRecord
from pyOAIMH.OAIHarvester import OAIHarvester
from pyOAIMH.OAIHarvester import HTTPLibError, ServerError

from pyOAIMH.MyXMLLib import MyXMLLib


from OFS.SimpleItem import Item

import random
from DateTime import DateTime

import zOAISupport  # for processId

manage_addOAIExistHarvesterForm = HTMLFile('dtml/manage_addOAIExistHarvesterForm', globals())

def manage_addOAIExistHarvester(self, id="", host="", url="", title="", days=7, oai_set='', exist_col='', create_exist_coll='', REQUEST=None, RESPONSE=None):
    """ method for adding a new Exist OAI object """
 
    if url=="" and host=="":
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'You%20need%20to%20specify%20an%20url%20and%20a%20host.')
            return None

           
    try:
        if id.strip() != '':
            id = zOAISupport.processId(id)
        else:
            id = zOAISupport.processId(host)
        OAIS = zOAIExistHarvester(id, host, url, title, days, oai_set, exist_col, create_exist_coll)
    except:
        import traceback
        traceback.print_exc()
        
    self._setObject(id, OAIS)
    OAIS = getattr(self, id)
    
    OAIS.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')




class zOAIExistHarvester(OAIHarvester, MyXMLLib, App.Management.Navigation, Item, Persistent, Implicit):
    """ """

    meta_type = 'Exist Open Archive Harvester'
    default_document = 'index_html'
    default_encoding = 'UTF-8'

    manage_options= (
        {'label': 'Preferences',     
         'action': 'manage_preferences' 
         },
        
        {'label': 'Update',     
         'action': 'manage_update'
         },

        )

    
    def __init__(self, id, host, url, title, days, oai_set, exist_col, create_exist_coll):
        """ """

        try:
            OAIHarvester.__init__(self, host, url, oai_set)
        except:
            # this is needed for some reason when python
            # version is < 2.2
            OAIHarvester.__init__.im_func(self, host, url, oai_set)
        
        self.id = id
        self.title = title
        self.dc2lom = 0

        # update frequency in days
        self.update_period = days
        
        # exist storage collection
        self.exist_col = exist_col
        self.create_exist_coll = create_exist_coll

    def manage_afterAdd(self, item, container):
        """ redef """
        # exist storage collection
        eXAgg = self.get_myContainer()
        eda = eXAgg.get_eXistDA()
        
        if not self.exist_col:
            self.exist_col = eXAgg.getExistCollRoot()+'/'+self.id
        if self.create_exist_coll:
            eda.createColl(self.exist_col)

    def manage_beforeDelete(self, item, container):
        """ redef """
        # We don't remove the collection due the fact the user can do it manually in the preference tab
        # Collection delete
        #eXAgg = self.get_myContainer()
        #eda = eXAgg.get_eXistDA()
        #eda.delColl(eXAgg.getExistCollRoot()+'/'+self.id)
        
    def get_exist_col(self):
        """
        """
        if not hasattr(self, 'exist_col'):
            self.exist_col = self.get_myContainer().getExistCollRoot()+'/'+self.id
        return self.exist_col
        
    def set_exist_col(self, col=''):
        """
        """
        self.exist_col = col
               
    def get_dc2lom(self):
        """ return dc2lom attribute """
        if hasattr(self,'dc2lom'):
            return self.dc2lom
        return 0
        
    def set_dc2lom(self,dc2lom = 0):
        """ set dc2lom attribute """
        self.dc2lom = dc2lom
            
    def get_locationTransform(self):
        """ return locationTransform attribute """
        if hasattr(self,'locationTransform'):
            return self.locationTransform
        return ''

    def set_locationTransform(self, locationTransform=''):
        """ set locationTransform attribute """
        self.locationTransform = locationTransform

    def get_keywordSep(self):
        """ return keywordSep attribute """
        if hasattr(self,'keywordSep'):
            return self.keywordSep
        return ''

    def set_keywordSep(self, keywordSep=''):
        """ set keywordSep attribute """
        self.keywordSep = keywordSep
        
    def get_replaceThis(self):
        """ return replaceThis attribute """
        if hasattr(self,'replaceThis'):
            return self.replaceThis
        return ''

    def set_replaceThis(self, replaceThis=''):
        """ set replaceThis attribute """
        self.replaceThis = replaceThis
        
    def get_replaceBy(self):
        """ return replaceBy attribute """
        if hasattr(self,'replaceBy'):
            return self.replaceBy
        return ''

    def set_replaceBy(self, replaceBy=''):
        """ set keywordSep attribute """
        self.replaceBy = replaceBy
        
    
    def get_myContainer(self):
        """ get my parent container """
        return self.aq_parent

    def handle_addOAIRecord(self, dom=None):
        """
        create or update <record> given its DOM node
        """
       
        # get record header
        #
        
        ## extract some informations from the DOM to process them after
        header = None
        id = None
        for h in dom.childNodes:
            if hasattr(h, 'tagName') and h.tagName == 'header':
                header = h
                for tag in header.childNodes:
                    if hasattr(tag, 'tagName') and tag.tagName == 'identifier':
                       id = tag
                       break
                break

        if header == None:
            raise "no header in", dom.toxml(self.default_decoding)
            
        # Use the id as the name for the zope record
        if id == None:
            raise "no identifier in ", dom.toxml(self.default_decoding)
        else:
            identifier = self.getDOMElementText(id, encode=self.default_encoding)
        
        if not identifier:
            # create a random record but dangerous because we will not overwrite it the last time we harvest MD
            identifier = str(DateTime().millis()) + str(random.randint(1, 10000))  
             
        metadata_format = self.current_request['metadataPrefix'].encode(self.default_encoding)
        identifier = string.strip(identifier)
        
        ressource_identifier = identifier.encode(self.default_encoding)

        if self.get_dc2lom() and metadata_format=="oai_dc":
            md_format_identifier = "oai_dc2lom"
        else:
            md_format_identifier = metadata_format
            
        try:
            # IL Y A UN PROBLEME D'ENCODAGE SUR CERTAIN CE QUI FAIT PLANTER LA MOISSON !!!!!!!
            identifier = ressource_identifier + '-' + md_format_identifier
        except:
            # GENERE UN PROBLEME D'ENCODAGE A L'AFFICHAGE !!!!!!
            identifier = identifier+'-'+md_format_identifier
        identifier = zOAISupport.processId(identifier)

        nsInfos = self.get_namespaceInfoByPrefix(metadata_format)
        rootNode = nsInfos.get('rootNode', '')
        # take the first "possibleRootNode" for oai rootNode replacement --> eXist storage
        newRootNode = nsInfos.get('possibleRootNode', [])[0]
        if rootNode:
            try:
                metadataDom = dom.getElementsByTagName('metadata')[0]
            except:
                metadataDom = dom
                
            metadataNode = None
            for child in metadataDom.childNodes:
                if child.localName == rootNode:
                    metadataNode = child
                    break               
            if metadataNode is None:
                print "no MD found in ", metadataDom.toxml(self.default_encoding) 
                return
        else:
            raise "no rootNode found, please check your configuration"

            
        xmlBody = ''
        for child in metadataNode.childNodes:
            xmlBody += child.toxml(self.default_encoding)
            
        nsDec = ""
        for nsd in nsInfos.get('nsDeclaration', []):
            nsDec += " xmlns:" + nsd
            
        nsDec += " " + nsInfos.get('mainNsDeclaration', '')
            
        newXML = """<?xml version="1.0" encoding="%(encoding)s"?>
        <%(tag)s %(nsDec)s>
          %(xmlBody)s
        </%(tag)s>""" % { 'encoding':self.default_encoding,
                          'tag':newRootNode,
                          'nsDec':nsDec,
                          'xmlBody':xmlBody,
                          }
       
        if self.get_dc2lom() and metadata_format=="oai_dc":
            if self.get_replaceThis():
               newXML = newXML.replace(self.get_replaceThis(), self.get_replaceBy())
            # tranformation de la MD en LOM depuis DC pour GA-Media support
            newXML = self.convertDCtoLOM(dc_xml=newXML, md_identifier=ressource_identifier)

        # the only thing to do is to save record in eXistDB
        eXAgg = self.get_myContainer()
        eda = eXAgg.get_eXistDA()
        nomXML = 'xmldb:exist://' + eda.server + ":" + eda.port + self.exist_col+'/'+identifier
        try:
            error = eda.saveDoc(newXML, nomXML, overwrite=1, object_only = 1)
        except:
            # error so we test if it's only if the target collection doesn't exists
            if not self.testCollection(self.exist_col):
               # we create it
               self.createCollection(self.exist_col)
               try:
                  error = eda.saveDoc(newXML, nomXML, overwrite=1, object_only = 1)
               except:
                  # it was not a collection problem
                  pass
            #import traceback
            #traceback.print_exc()
            pass

    ######################
    ####  eXist management
    ######################
    
    def testCollection(self, collPath=''):
        """
        """
        # exist storage collection
        if not collPath:
            return 0
        eXAgg = self.get_myContainer()
        eda = eXAgg.get_eXistDA()
        return eda.isCollection(collPath)

    def createCollection(self, collPath=''):
        """
        """
        # exist storage collection
        if not collPath:
            return 0
        eXAgg = self.get_myContainer()
        eda = eXAgg.get_eXistDA()
        return eda.createColl(collPath)

    def removeCollection(self, collPath=''):
        """
        """
        # exist storage collection
        if not collPath:
            return 0
        eXAgg = self.get_myContainer()
        eda = eXAgg.get_eXistDA()
        return eda.delColl(collPath)
        
    ######################
    ####  ZMI Interfaces
    ######################

    #manage_main = HTMLFile("dtml/manage_OAIHarvesterMainForm",globals())

    
    manage_preferences = HTMLFile("dtml/manage_OAIHarvesterPrefsForm",globals())
    manage_update = HTMLFile("dtml/manage_OAIHarvesterUpdateForm",globals())
    manage_main = HTMLFile("dtml/manage_OAIHarvesterUpdateForm",globals())

    def manage_OAIHarvesterPrefs(self, title, minutes, site_host, site_url, oai_set='', dc2lom='0', locationTransform='', keywordSep='', replaceThis='', replaceBy='', exist_col='', deleteColl='0', emptyColl='0', createColl='0', REQUEST=None, RESPONSE=None):
        """ save preferences """

        self.title = title
        self.update_period = minutes
        self.set_siteURL(site_url)
        self.set_siteHost(site_host)
        self.set_oaiSet(oai_set)
        self.set_dc2lom(int(dc2lom))
        self.set_locationTransform(locationTransform)
        self.set_keywordSep(keywordSep)
        self.set_replaceThis(replaceThis)
        self.set_replaceBy(replaceBy)
        
        self.set_exist_col(exist_col)
        
        if createColl=='1':
            self.createCollection(self.get_exist_col())
        if emptyColl=='1':
            self.removeCollection(self.get_exist_col())
            self.createCollection(self.get_exist_col())
        if deleteColl=='1':
            self.removeCollection(self.get_exist_col())

        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')

        
    def set_oaiSet(self, oai_set):
        """set oai set"""
        self.oai_set = oai_set
    
    def get_oaiSet4html(self):
        """
        """
        if not self.oai_set:
            return ""
        return self.oai_set

    def manage_OAIHarvesterUpdate(self, REQUEST=None, RESPONSE=None):
        """ update site records, identification """

        try:
            self.do_updateSite()
            RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Site%20records%20updated')
        except (HTTPLibError, ServerError):
            # import sys
            # print sys.exc_type; sys.exc_value
            
            RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Problem%20connecting%20to%20site')

    


