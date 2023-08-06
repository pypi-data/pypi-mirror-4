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

manage_addOAIExistSetForm = HTMLFile('dtml/manage_addOAIExistSetForm', globals())

def manage_addOAIExistSet(self, title=None,
                                REQUEST=None):
    """ method for adding a new OAI eXist namespace """

    # print "in manage add OAI Namespace", self

    try:
        id = zOAISupport.processId(title)
        OAI_SET = zOAIExistSet(id, title)
    except:
        import traceback
        traceback.print_exc()
        RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20un%20titre')
        return None

    self._setObject(id, OAI_SET)
    # get back OAI Record object
    #
    OAI_SET = getattr(self, id)
    OAI_SET.initialize()
    
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')


class zOAIExistSet(App.Management.Navigation, SimpleItem, Implicit):
    """ """

    meta_type = 'Exist Open Archive Set'
    default_document = 'index_html'

    manage_options = (
        {'label': 'Information',     
         'action': 'index_html' 
         },
        )

    index_html = HTMLFile("dtml/manage_OAIExistSetUpdateForm",globals())


    def __init__(self,
                 id,
                 setName):
        """ """

        self.id = id  
        
        self.setSpec = ""
        self.setName = setName
        self.setDescription = ""
        self.setXPath = {}


    def initialize(self):
        """ """
        pass   

    def get_setSpec(self):
        """
        """
        return self.setSpec
    
    def get_setName(self):
        """
        """
        return self.setName
        
    def get_setDescription(self):
        """
        """
        return self.setDescription
        
    def get_setXPath(self):
        """
        """
        return self.setXPath
        
    def manage_OAIExistSetUpdate(self,
            setName,
            setSpec,
            setDescription,
            REQUEST=None):
        """ """
        self.setSpec = setSpec
        self.setName = setName
        self.setDescription = setDescription
        for ns in self.get_myNamespaceStorage().objectValues('Exist Open Archive Namespace'):
            prefix = ns.get_nsDictionary().get('prefix', '')
            self.setXPath[prefix] = REQUEST.get(prefix +"_xfilter", "")

        REQUEST.RESPONSE.redirect(self.absolute_url() + '/index_html?manage_tabs_message=Set%20has%20been%20updated')
        
    def get_setNSXPath(self, nsPrefix=""):
        """
        """
        return self.setXPath.get(nsPrefix, '*') or '*'




        
    
