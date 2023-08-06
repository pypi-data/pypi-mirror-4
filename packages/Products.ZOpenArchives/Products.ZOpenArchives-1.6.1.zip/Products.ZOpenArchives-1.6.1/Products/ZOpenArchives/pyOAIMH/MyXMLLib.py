# -*- coding: iso-8859-15 -*-

import string
# file with helpful XML/DOM methods

import xml.dom.minidom

import re

class MyXMLLib:
    """ """

    def getDOMElementText(self, dom_node=None, encode=None):
        """
        input is a DOM node

        returns text of node; encoded text if
          encode parameter is given
        """
        # print dom_node, encode
        text = ""
        for node in dom_node.childNodes:
            if node.nodeType == node.TEXT_NODE:
                text = text + string.strip(node.data)
        if encode != None:
            text = text.encode(encode)
        return text.strip()

    def findDOMElements(self, dom_list=[], tag_path=[]):
        """
        finds DOM elements in DOM trees by path
        path is a list of strings - eg, [ 'Adressbook','Adress','Person','Name']
        which corresponds to tag names in XML

        returns list of nodes which have this path, or [] for none
        """
        found_nodes = []
        if len(dom_list)==0 or len(tag_path)==0:
            return found_nodes

        # get next tag to search for
        #
        tag_name = tag_path[0]
        new_path = tag_path[1:]

        # print "findDOMElents", tag_name

        # find all matching nodes
        #
        for dom in dom_list:
##            for node in dom.getElementsByTagName(tag_name):
##                found_nodes.append(node)
            for node in dom.childNodes:
                if hasattr(node, 'tagName') and node.tagName == tag_name:
                    found_nodes.append(node)

        # print "found %s elements\n\n" % len(found_nodes)

        if len(new_path):
            found_nodes = self.findDOMElements(dom_list=found_nodes,tag_path=new_path)

        return found_nodes

    def convertDCtoLOM(self, dc_xml='', md_identifier='', REQUEST=None):
        """
        Convert a dc MD to LOM
        """
        dom = xml.dom.minidom.parseString(dc_xml)
        dicoDC = {'md_identifier': md_identifier}
        paths = { 'title': ['dc:dc','dc:title'],
                  'subject': ['dc:dc','dc:subject'],
                  'description': ['dc:dc','dc:description'],
                  'creator': ['dc:dc','dc:creator'],
                  'author': ['dc:dc','dc:author'],
                  'type': ['dc:dc','dc:type'],
                  'publisher': ['dc:dc','dc:publisher'],
                  'contributor': ['dc:dc','dc:contributor'],
                  'date': ['dc:dc','dc:date'],
                  'format': ['dc:dc','dc:format'],
                  'identifier': ['dc:dc','dc:identifier'],
                  'source': ['dc:dc','dc:source'],
                  'language': ['dc:dc','dc:language'],
                  'relation': ['dc:dc','dc:relation'],
                  'coverage': ['dc:dc','dc:coverage'],
                  'rights': ['dc:dc','dc:rights'],
                }


        if not dom:
            return None
        for key in paths:
            txt_list = []
            for text_dom in self.findDOMElements( dom_list=[dom], tag_path=paths[key] ):
                txt = self.getDOMElementText(dom_node=text_dom, encode=self.default_encoding)
                if key == 'identifier' and self.get_locationTransform():
                    txt = self.applyRE(txt.strip(), self.get_locationTransform())
                if txt:
                    txt_list.append(txt.replace('&', '&#38;'))
                    if key == 'identifier' and self.get_locationTransform():
                        break
            dicoDC[key] = ' '.join(txt_list)

        if self.get_keywordSep():
            kws = dicoDC['subject'].split(self.get_keywordSep())
        else:
            kws = [dicoDC['subject']]
        kws_lom = ""
        for k in kws:
            kws_lom += LOM_KEYWORD_TEMPLATE % (dicoDC['language'], k.strip())

        dicoDC['keywords'] = kws_lom


        return LOM_TEMPLATE % dicoDC

    def applyRE(self, text="", re_expr=""):
        """
        apply the re to the text and return the result
        """
        if not re_expr:
            return text
        monExpr = re.compile(re_expr, re.MULTILINE | re.DOTALL)
        res = monExpr.findall(text)
        if res:
            return res[0]
        return ''


LOM_KEYWORD_TEMPLATE =  """<lom:keyword>
                    <lom:string language="%s">%s</lom:string>
                </lom:keyword>"""

LOM_TEMPLATE="""<?xml version="1.0" ?>
     <lom:lom xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:lom="http://ltsc.ieee.org/xsd/LOM" xsi:schemaLocation="http://www.pentila.com/xsd/LOM http://www.pentila.com/LOMSchema/lom.xsd">
            <lom:general>
                <lom:identifier>
                    <lom:catalog>ID</lom:catalog>
                    <lom:entry>%(md_identifier)s</lom:entry>
                </lom:identifier>
                <lom:title>
                    <lom:string language="%(language)s">%(title)s</lom:string>
                </lom:title>
                <lom:description>
                    <lom:string language="%(language)s">%(description)s</lom:string>
                </lom:description>
                %(keywords)s
                <lom:coverage>
                    <lom:string language="%(language)s">%(coverage)s</lom:string>
                </lom:coverage>
                <lom:language>%(language)s</lom:language>
                <lom:structure>
                    <lom:source>LOMv1.0</lom:source>
                    <lom:value>linear</lom:value>
                </lom:structure>
            </lom:general>
            <lom:lifeCycle>
                <lom:contribute>
                    <lom:role>
                        <lom:source>LOMv1.0</lom:source>
                        <lom:value>author</lom:value>
                    </lom:role>
                    <lom:entity>%(author)s</lom:entity>
                </lom:contribute>
                <lom:contribute>
                    <lom:role>
                        <lom:source>LOMv1.0</lom:source>
                        <lom:value>publisher</lom:value>
                    </lom:role>
                    <lom:entity>%(publisher)s</lom:entity>
                </lom:contribute>
                <lom:contribute>
                    <lom:role>
                        <lom:source>LOMv1.0</lom:source>
                        <lom:value>contributor</lom:value>
                    </lom:role>
                    <lom:entity>%(contributor)s</lom:entity>
                    </lom:contribute>
                <lom:contribute>
                    <lom:role>
                        <lom:source>LOMv1.0</lom:source>
                        <lom:value>creator</lom:value>
                    </lom:role>
                    <lom:entity>%(creator)s</lom:entity>
                    <lom:date>
                        <lom:dateTime>%(date)s</lom:dateTime>
                    </lom:date>
                </lom:contribute>
            </lom:lifeCycle>
            <lom:educationnal>
                <lom:learningResourceType>
                    <lom:source>LOMv1.0</lom:source>
                    <lom:value>%(type)s</lom:value>
                </lom:learningResourceType>
            </lom:educationnal>
            <lom:technical>
                <lom:format>%(format)s</lom:format>
                <lom:location>%(identifier)s</lom:location>
            </lom:technical>
            <lom:rights>
                <lom:copyrightAndOtherRestrictions>
                    <lom:source>LOMv1.0</lom:source>
                    <lom:value>yes</lom:value>
                </lom:copyrightAndOtherRestrictions>
                <lom:description>
                    <lom:string language="%(language)s">%(rights)s</lom:string>
                </lom:description>
            </lom:rights>
            <lom:relation>
                <lom:resource>
                    <lom:identifier>
                        <lom:catalog>URI</lom:catalog>
                        <lom:entry>%(relation)s</lom:entry>
                    </lom:identifier>
                </lom:resource>
            </lom:relation>
            <lom:relation>
                <lom:kind>isbasedOn</lom:kind>
                <lom:resource>
                    <lom:identifier>
                        <lom:catalog>URI</lom:catalog>
                        <lom:entry>%(source)s</lom:entry>
                    </lom:identifier>
                </lom:resource>
            </lom:relation>
        </lom:lom>
"""
