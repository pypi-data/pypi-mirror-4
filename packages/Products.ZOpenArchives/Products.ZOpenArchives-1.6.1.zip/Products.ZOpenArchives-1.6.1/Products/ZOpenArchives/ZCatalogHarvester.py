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
from Globals import HTMLFile, Persistent
from Products.ZCatalog.ZCatalog import ZCatalog
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
import zOAIRecord   # for manage_addOAIRecord
from zOAIRecord import create_ObjectMetadata
import xml.dom.minidom

from Products.ZCatalog.ZCatalog import ZCatalog
import zOAISupport  # for processId
import sys

manage_addZCatalogHarvesterForm = HTMLFile('dtml/manage_addZCatalogHarvesterForm', globals())

def manage_addZCatalogHarvester(self, id="", title="Zope OAI Server", update_period=None, autopublish=1, autopublishRoles = [], REQUEST=None, RESPONSE=None):
    """ method for adding a new Zope OAI Server """

    if id == '':
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20un%20titre')
            return None
    id = 'OAI_' + id    
    try:
        ZCATO = ZCatalogHarvester(id, title, update_period, autopublish, autopublishRoles)
    except:
        import traceback
        traceback.print_exc()
        
    self._setObject(id, ZCATO)
    ZCATO = getattr(self, id)
    ZCATO.initialize()
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')



class ZCatalogHarvester(App.Management.Navigation,BTreeFolder2, Persistent, Implicit):
    """
    name of catalog to index
    """
    
    meta_type = 'ZCatalog Harvester'
    default_document = 'index_html'

    default_catalog = 'OAI_Catalog'
    default_encoding = 'UTF-8'


    manage_options= (
        {'label': 'Contents',     
         'action': 'manage_main'
         },

        {'label': 'Preferences',     
         'action': 'manage_preferences' 
         },
        
        {'label': 'Update',     
         'action': 'manage_update' 
         },
        )

    def __init__(self, id, title, update_period, autopublish, autopublishRoles):
        """
        id of harvester is OAI_ + name of catalog
          to index  eg, 'OAI_site_index'
        """
        BTreeFolder2.__init__(self,id)

        self.id = id
        self.title = title

        # default period to check - minutes
        # 
        self.update_period = update_period
        self.last_update = None
        self.autopublish = autopublish
        self.autopublishRoles = filter(None, autopublishRoles)
        self.force_update = 1

        self.metadata_prefix = None


    def initialize(self):
        """
        set generic metadata prefix
        """
        #print "### in init zcatalog harvester"
        self.last_update = None
        self.metadata_prefix = 'oai_dc'
        self.allowedRoles = ['Anonymous']
        self.update_ZCatalogHarvester()
        self.add_oai_index()
        
        

    def index_html(self, REQUEST=None, RESPONSE=None):
        """
        main method for the OAI server. processes
          all incoming URL requests
        get args from request form
        """
        self.the_request = REQUEST.URL0
        return self.process_Request(args=REQUEST.form)    
 

    def get_myContainer(self):
        """ get my parent container """

        #print "### get my container"

        # need to do this loop because having problems
        #   getting the real parent - like when adding
        #   a new object to a server
        #
        while (1):
            # print "trying... "
            parent = self.aq_parent
            if parent.id != 'ZOpenArchives':
                break
            self = parent

        # print "parent ", parent.id, parent.meta_type
        return parent


    def get_theSiteCatalog(self):
        """
        get the catalog in the portail site
        looking for the one with same name as this object
        """
        #print "### get site catalog"

        catalog = getattr( self.get_myContainer().get_myContainer(), self.id[4:] )
        # print catalog.id, catalog.meta_type
        return catalog
  
    def add_oai_index(self):
        """
        add the oai index to the site catalog
        chosen to publish
        index all items
        """
        cat = self.get_theSiteCatalog()
        
        try:
            cat.addIndex('oai_state', 'FieldIndex')
            cat.manage_reindexIndex(ids='oai_state')
        except:
            pass
          
    def delete_oai_index(self):
        """
        delete the index from the site catalog
        chosen to publish
        """
        cat = self.get_theSiteCatalog()
        cat.delIndex('oai_state')
          

    def update_ZCatalogHarvester(self):
        """
        get cataloged objects, set update time, re-index
        """
        # print "### udpate zcatalog harvester"
        self.last_update = DateTime.DateTime()
        self.update_CatalogItems()
        self.reindex_object()

    def update_CatalogItems(self):
        """ update get all items in catalog """
        
        # print "### in update_CatalogItems"
 
        # always do manual publish - in case someone adds other
        #   information that they want shared, other than what
        #   autopublish provides
        #
        # self.process_Manualpublish()

        if self.autopublish == 1:
            self.process_Autopublish()

        # now look for objects which have been
        #  deleted in the portal catalog
        #
        self.process_deletedObjects()


    def delete_Records(self):
        """ sometimes it's necessary to clean out the records """
        self.manage_delObjects( ids = self.objectIds('Open Archive Record') )
        
            
    def process_Autopublish(self):
        """
        method to process all objects in the Portal catalog
        just uses Dublin Core
        """
        # print "### in process_Autopublish"


        # override portal_catalog searchResults, use directly
        #   that of ZCatalog
        #
        searchDict = {'allowedRolesAndUsers':self.autopublishRoles}
        for item in ZCatalog.searchResults( self.get_theSiteCatalog(), searchDict ):

            # print "## working on an item ", item.id
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
            path = urllib.unquote( '/' + obj.absolute_url(1) + '-oai_dc'  )
            pid = zOAISupport.processId(path)
            OAIO = self._getOb( pid, None)

            
            # check to see if we need to update the object, either
            #   - it has been updated since last time
            #   - force update is specified
            #   - if it is a new object
            #
            update = 0
            if self.last_update.greaterThan(obj.bobobase_modification_time()):
                update = 1
                
            if self.force_update == 1:
                update = 1

            if OAIO == None:
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
                ns_dict = self.get_myContainer().get_namespaceInfoByPrefix('oai_dc')

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
            
            if OAIO != None:
                # print "updating oaio", OAIO.id
                OAIO.update_Record(xml=record_xml)
            else:
                # print "adding oaio", OAIO.id
                zOAIRecord.manage_addOAIRecord(self, metadata_format='oai_dc', id=pid, xml=record_xml)

        # outside of loop
        self.force_update = 0


            
    def process_Manualpublish(self):
        """
        need to create different types of objects depending
        on the various types of metadata associated with
        the original object - this is for the cataloging
        and quick serving of information
        """
        # print "#### in manual publish"
        searchDict = {'oai_state':'shared'}

        # override portal_catalog searchResults, use directly
        #   that of ZCatalog
        #
        for item in ZCatalog.searchResults( self.get_theSiteCatalog(), searchDict ):

            # print "## working on an item ", item.id
            # get object and create its metadata structure
            #   check to make sure that the object still exists
            #   not just the reference in the catalog
            #
            obj = item.getObject()
            if obj == None:
                print "Error: not found in process_Manualpublish", item.id
                continue

            available_metadata = obj.get_metadataTypes()
            # print "have these ", available_metadata

            for metadata in available_metadata:
                
                # take each one, check if exists

                # see if the harvester already has the object
                #   decide whether to update or add new one
                #            
                path = urllib.unquote( '/' + obj.absolute_url(1) + '-' + metadata )
                # print "searching for ", path
                pid = zOAISupport.processId(path)
                OAIO = self._getOb( pid, None)


                # check to see if we need to update the object
                #   - been updated since last time
                #   - need to force update
                #   - if the object is new
                #
                update = 0
                if self.last_update.greaterThan(obj.bobobase_modification_time()):
                    update = 1

                # print "force ", self.force_update
                if self.force_update == 1:
                    update = 1

                if OAIO == None:
                    update = 1

                if update == 0:
                    # we don't create new XML, but we still have
                    #   to call the update to the zOAIRecord so
                    #   that it doesn't get marked as 'deleted'
                    #
                    # print "no changed record"
                    record_xml = None
                else:
                    # print "changed record"
                    # get all namespaces for this object
                    # they are used for searching the XML tags
                    #
                    # get xml and create dom

                    # TODO: capture error
                    record_dom = obj.get_metadataDOM(prefix=metadata)
                    print 
                    # record_dom = xml.dom.minidom.parseString(record_xml)
                    from_meta_node = record_dom

                    # print "in create_ObjectMetadataXML"
                    # print "with enc ", def_enc
                    # start XML record
                    xmldoc = xml.dom.minidom.Document()

                    # xmldoc.createProcessingInstruction('xml', 'version="1.0" encoding="%s"' % self.default_encoding )

                    # create <record> node
                    n_record = xmldoc.createElement("record")
                    xmldoc.appendChild(n_record)
              

                    # ###############
                    # add <header>
                    #
                    n_header = xmldoc.createElement("header")
                    n_record.childNodes.append(n_header)

                    # add child <identifier> 
                    h_id = xmldoc.createElement('identifier')
                    n_header.appendChild(h_id)

                    # TODO: put oai name in attribute
                    site_domain = self.get_myContainer().repositoryDomain()
                    id =  'oai:'+ site_domain + ':' + '/' + obj.absolute_url(1)
                    id = urllib.unquote(id)
                    h_id.appendChild(xmldoc.createTextNode(id))

                    h_date = xmldoc.createElement('datestamp')
                    n_header.appendChild(h_date)

                    date = self.get_myContainer().get_fixedDate(str(obj.bobobase_modification_time()))
                    h_date.appendChild(xmldoc.createTextNode(date))


                    # ####################
                    # add <metadata> tag
                    #
                    n_metadata = xmldoc.createElement("metadata")
                    n_record.childNodes.append(n_metadata)
                    to_meta_node = n_metadata

                    c2 = from_meta_node.cloneNode(1)
                    to_meta_node.appendChild(c2)
                    
                    record_xml =  xmldoc.toxml(self.default_encoding)

                # print "record ", record_xml 
                if OAIO != None:
                    #print "updating oaio", OAIO.id
                    OAIO.update_Record(xml=record_xml)
                else:
                    # TODO : add proper
                    zOAIRecord.manage_addOAIRecord(self, metadata_format=metadata, id=pid, xml=record_xml)

        # outside of loop
        self.force_update = 0



    def process_deletedObjects(self):
        """
        """
        # print "### process deleted objects"
        # look for items not updated, and mark as deleted
        #
        catalog = getattr( self.get_myContainer(), self.default_catalog )
        for item in catalog.searchResults( {'last_update':self.last_update,
                                            'last_update_usage':'range:max',
                                            'status':'available'} ):
            
            record = item.getObject()
            if record == None:
                # print "object not found in process_ManualPublish ", item.id
                continue

            # TODO: deleted record support - yes, no, transient
            #
            record.mark_recordDeleted()


        
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

            

    ####
    #### OBJECT MANAGEMENT STUFF
    ####


    #manage_main = HTMLFile("dtml/manage_OAIHarvesterMainForm",globals())

    
    manage_preferences = HTMLFile("dtml/manage_ZCatalogHarvesterPrefsForm",globals())

    def manage_ZCatalogHarvesterPrefs(self, title, update_period,autopublish, autopublishRoles=[], REQUEST=None, RESPONSE=None):
        """ save preferences """

        self.title = title
        if self.autopublish != autopublish:
            self.autopublish = autopublish
            self.delete_Records()

        self.autopublishRoles = filter(None, autopublishRoles) 
        self.update_period = update_period
        self.force_update = 1
   
        self.reindex_object() # need to recatalog update_period

        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')



    manage_update = HTMLFile("dtml/manage_ZCatalogHarvesterUpdateForm",globals())

    def manage_ZCatalogHarvesterUpdate(self, REQUEST=None, RESPONSE=None):
        """ update catalog records """
 
        # TODO: update will also need to check
        #   existing records for deletions on server, etc
        self.update_ZCatalogHarvester()
        # self.handle_deletedObject()

        RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Site%20records%20updated')

    def manage_beforeDelete(self, item, container):
        """ """
        # self.delete_oai_index()
        self.unindex_object()
        
        BTreeFolder.inheritedAttribute("manage_beforeDelete")(self,item,container)

        
    def commit_Changes(self):
        """ """
        self._p_changed = 1

