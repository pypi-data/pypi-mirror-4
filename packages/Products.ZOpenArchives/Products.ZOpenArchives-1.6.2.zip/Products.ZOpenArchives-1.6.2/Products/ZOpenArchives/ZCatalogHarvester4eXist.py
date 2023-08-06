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

__doc__ = """ Produit ZCatalog Harvester """


import urllib
import string
import DateTime
import App
from Globals import HTMLFile, DTMLFile
from Products.ZCatalog.ZCatalog import ZCatalog
from AccessControl import ClassSecurityInfo
from zOAIExistHarvester import zOAIExistHarvester
from zOAISupport import processId
from zOAIRecord import create_ObjectMetadata
import xml.dom.minidom

import zOAISupport  # for processId
import sys

from zOAIExistNamespace import oai_dc_defaults, oai_lom_defaults

supported_metadataOAI = {
                    'OAI DC':'oai_dc',
                    'OAI LOM':'lom'
                    }

manage_addZCatalogHarvester4eXistForm = HTMLFile('dtml/manage_addZCatalogHarvester4eXistForm', globals())

def manage_addZCatalogHarvester4eXist(self, id = '', catId="", title="ZCatalog OAI 4 eXist", metadataPrefix = 'oai_dc', update_period = None, searchingAllowedRolesAndUsers = [], oai_set = None, exist_col='', create_exist_coll='', REQUEST=None, RESPONSE=None):
    """ method for adding a new Zope OAI Server """

    if id == '':
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?manage_tabs_message=Vous%20devez%20choisir%20un%20identifiant')
            return None
    else:
        id = processId(id)
        
    if catId == '':
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?manage_tabs_message=Vous%20devez%20choisir%20un%20Catalogue')
            return None
    
    objCat = self.unrestrictedTraverse('/'+catId)
    if objCat is None:
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?manage_tabs_message=Le%20catalogue%20est%20inaccessible')
            return None
    if type(metadataPrefix) is not type([]):
        metadataPrefix = [metadataPrefix]
    try:
        ZCATO = ZCatalogHarvester4eXist(id, catId, title, metadataPrefix, update_period, searchingAllowedRolesAndUsers, oai_set, exist_col, create_exist_coll)
    except:
        import traceback
        traceback.print_exc()
        
    self._setObject(id, ZCATO)

    ZCATO = getattr(self, id)
    ZCATO.initialize()
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1&manage_tabs_message=Harvester%20added')


class ZCatalogHarvester4eXist(zOAIExistHarvester):
    """
    name of catalog to index
    """
    
    meta_type = 'ZCatalog Harvester 4 eXist'
    manage_preferences = HTMLFile("dtml/manage_OAIHarvester4eXistPrefsForm",globals())
    
    manage_options= (
        {'label': 'Update',     
         'action': 'manage_update'
         },
         {'label': 'Preferences',     
         'action': 'manage_preferences' 
         },)


    def __init__(self, id, catId, title, metadataPrefix, update_period, searchingAllowedRolesAndUsers, oai_set, exist_col, create_exist_col):
        """
        id of harvester is OAI_ + name of catalog
          to index  eg, 'OAI_site_index'
        """
        zOAIExistHarvester.__init__(self, id, '', '', title, update_period, oai_set, exist_col, create_exist_col)

        # default period to check - minutes
        # 
        self.searchingAllowedRolesAndUsers = filter(None, searchingAllowedRolesAndUsers)

        self.metadata_prefix = metadataPrefix
        self.catId = catId
        
        # outside of loop
        self.force_update = 1
        
    def initialize(self):
        """
        issue_Identify - get OAI site information from URL
        """
        self.issue_Identify()
        
    def do_updateSite(self):
        """
        get updates from site - Identify, ListMetadataFormats, ListRecords
        """

        # TODO: update will also need to check
        #   existing records for deletions on server, etc

        self.set_siteStatus('lastRequest', DateTime.DateTime().aCommon())
    
        self.issue_Identify()
        self.issue_ListMetadataFormats()
        #### add by jecez for manage oai_dc prefix in portal #################
        namespaces = getattr(self.aq_parent,'Namespaces')
        lNameSpaceMetaDataPrefix = []
        for nm in namespaces.objectValues():
            lNameSpaceMetaDataPrefix.append(nm.get_nsPrefix())
            
        #for metadata_prefix in self.site_metadata.keys():
        for metadata_prefix in  self.site_metadata.keys():
            #print "metadataPrefix", metadata_prefix
            if metadata_prefix in lNameSpaceMetaDataPrefix:
        ########## end ########################################################
                self.issue_ListRecords( oai_metadataPrefix = metadata_prefix, oai_set = self.oai_set )
        self.set_siteStatus('lastUpdate', DateTime.DateTime().aCommon())
        

    def update_OAIHarvester4eXistPrefs(self, title, update_period, catId = '', searchingAllowedRolesAndUsers = '', metadataPrefix = 'oai_dc', oai_set = None, exist_col='', deleteColl='0', emptyColl='0', createColl='0', REQUEST = None, RESPONSE = None):
        """ save preferences """

        self.title = title
        self.update_period = update_period
        if type(metadataPrefix) is not type([]):
            metadataPrefix = [metadataPrefix]
        self.metadata_prefix = metadataPrefix
        self.catId = catId
        self.oai_set = oai_set
        self.searchingAllowedRolesAndUsers = filter(None, searchingAllowedRolesAndUsers)
        
        self.set_exist_col(exist_col)
        
        if createColl=='1':
            self.createCollection(self.get_exist_col())
        if emptyColl=='1':
            self.removeCollection(self.get_exist_col())
            self.createCollection(self.get_exist_col())
        if deleteColl=='1':
            self.removeCollection(self.get_exist_col())
            
        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')


    def getMetadataPrefix(self):
        """ return metadata prefix """
        return self.metadata_prefix

    def getSupported_metadataOAI(self):
        """ return supported metadata prefix """
        return supported_metadataOAI

    def getRemoteCatalog(self):
        """ return the remote catalog """
        try:
            objCat = self.unrestrictedTraverse(self.catId)
            return objCat
        except:
            return None

    def issue_Identify(self):
        """
        method to issue the 'oai/?verb=Identify' request
        """
        objCat = self.getRemoteCatalog()
        if objCat is not None:
            self.set_siteStatus('status', 'Available')
        else:
            self.set_siteStatus('status', 'Unavailable')
            
        self.set_protocolVersion('2.0')

        self.set_repositoryName('Catalog %s repository' % objCat.id)

        # retrieve baseURL - single
        #
        self.set_baseURL(objCat.absolute_url())
        
        # retrieve adminEmail - multiple
        admin_list = []
        admin_list.append('zopeCatlaog@localhost.com')

        self.set_adminEmail(admin_list)


        # description - multiple (optional)
        #
        self.set_description('Zope WebSite Catalog')



        ## these are for 2.0
        
        # retrieve earliestDatestamp - single
        #
        self.set_earliestDatestamp('empty')
        
        # retrieve deletedRecord - single
        #
        self.set_deletedRecord('persistent')
        # granularity - single
        #
        self.set_granularity('YYYY-MM-DD')
        # compression - single (optional)
        #
        self.set_compression('N/A')

    def issue_ListMetadataFormats(self, oai_identifier=None):
        """
        This harvester 4 zope Catalog can return lom metadata and dc metadata
        You must overwrite this method if you want others md
        """
        # Process DC
        dict = {}
        dict['metadataNamespace'] = oai_dc_defaults['namespace']
        dict['metadataPrefix'] = oai_dc_defaults['prefix']
        dict['schema'] = oai_dc_defaults['schema']
        
        if dict['metadataPrefix'] in self.metadata_prefix:
            self.site_metadata[dict['metadataPrefix']]=dict
        # Process LOM
        dict = {}
        dict['metadataNamespace'] = oai_lom_defaults['namespace']
        dict['metadataPrefix'] = oai_lom_defaults['prefix']
        dict['schema'] = oai_lom_defaults['schema']
        if dict['metadataPrefix'] in self.metadata_prefix:
            self.site_metadata[dict['metadataPrefix']]=dict
            
    def issue_ListRecords(self, oai_metadataPrefix, oai_from=None, oai_until=None, oai_set=None, oai_setSpec=None ):
        """
        method to issue the 'oai/?verb=ListRecords&metadataPrefix=oai_dc'

        req args = metadataPrefix
        opt args = from, until, set (setSpec)
        exc args = resumptionToken
        
        get records from site
          create objects if necessary
          update ones which exist
          get next batch if more
        """
        self.current_request =  { 'verb':'ListRecords',
                                  'metadataPrefix':oai_metadataPrefix,
                                  'from':oai_from,
                                  'until':oai_until,
                                  'set':oai_set,
                                  'setSpec':oai_setSpec
                                  }
        searchDict = {'allowedRolesAndUsers':self.searchingAllowedRolesAndUsers}
        if oai_set:
            searchDict['path'] = oai_set
        else:
            searchDict['path'] = '/'
            
        try:
            resultSearch = ZCatalog.searchResults( self.getRemoteCatalog(), searchDict )
        except:
            return None
        for item in resultSearch:

            # get object and create its metadata structure
            #   check to make sure that the object still exists
            #   not just the reference in the catalog
            #
            try:
                obj = item.getObject()
            except:
                obj=None
            if obj == None:
                print "Error process_Autopublish: referenced object not found in catalog", item.id
                continue
            
            # see if the harvester already has the object
            #   decide whether to update or add new one
            #            
            path = urllib.unquote( '/' + obj.absolute_url(1))
            pid = zOAISupport.processId(path)

            
            # check to see if we need to update the object, either
            #   - it has been updated since last time
            #   - force update is specified
            #   - if it is a new object
            #
            update = 0
            if DateTime.DateTime(self.site_status['lastRequest']).greaterThan(obj.bobobase_modification_time()) or force_update==1:
                update = 1
     
            if update == 0:
                # we don't create new XML, but we still have
                #   to call the update to the zOAIRecord so
                #   that it doesn't get marked as 'deleted'
                #   None signals object is still there, but not changed
                #
                record_xml = None
            else:
                # get all namespaces for this object
                # they are used for searching the XML tags
                #
                ns_dict = self.get_myContainer().get_namespaceInfoByPrefix(oai_metadataPrefix)

                # create dictionary for object information
                #  to pass it into create_ObjectMetadata()
                #
                # TODO : use get_MetadataDictionary in metadataaware
                #
                obj_data = {}
                obj_data['header_tags'] = h_tags = {}
                obj_data['metadata_tags'] = m_tags = {}

                site_domain = self.get_myContainer().repositoryDomain()
                id =  'oai:'+ site_domain + ':' + '/' + obj.absolute_url(1)
                h_tags['identifier'] = urllib.unquote(id)
                h_tags['datestamp'] = self.get_myContainer().get_fixedDate(str(obj.bobobase_modification_time()))
                
                if ns_dict['rootNode'] == 'dc':
                    print "Dublin Core"
                
                m_tags['identifier'] = obj.absolute_url()
                
                if hasattr(obj, 'Title'):
                    title = obj.Title()
                else:
                    title = obj.title_or_id()
                m_tags['title'] = title
                
                if hasattr(obj, 'Description'):
                    description = obj.Description()
                else:
                    description = 'n/a'
                m_tags['description'] = description
                
                if hasattr(obj, 'Subject'):
                    subject = obj.Subject()
                else:
                    subject = 'n/a'               
                m_tags['subject'] = subject
                
                if hasattr(obj, 'Type'):
                    type = obj.Type()
                else:
                    type = obj.meta_type
                m_tags['type'] = type
                
                m_tags['date'] = self.get_myContainer().get_fixedDate(str(obj.bobobase_modification_time()))
                
                if hasattr(obj, 'Creator'):
                    creator = obj.Creator()
                else:
                    for user, roles in obj.get_local_roles():
                        if 'Owner' in roles:
                            creator = user
                            break
                m_tags['creator'] = creator
                

                

                # get object's metadata XML formattted to OAI specs
                #
                record_xml = create_ObjectMetadata(obj, obj_data, ns_dict=ns_dict,
                                                   type='xml', def_enc=self.default_encoding)
            
                dom = xml.dom.minidom.parseString(record_xml)
                self.handle_ListRecords([dom])

        # outside of loop
        self.force_update = 0
        
        
    def get_myContainer(self):
        """ return parent container """
        return self.aq_parent

            
                    

 
        


