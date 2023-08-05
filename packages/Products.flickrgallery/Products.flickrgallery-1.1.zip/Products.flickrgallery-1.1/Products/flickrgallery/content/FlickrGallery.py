# -*- coding: utf-8 -*-
#
# File: FlickrGallery.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 1.6.0-beta-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.flickrgallery.config import *

# additional imports from tagged value 'import
from Products.DataGridField import DataGridField
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.Column import Column
from Products.Archetypes.public import DisplayList

##code-section module-header #fill in your manual code here
from flickrengine import flickrengine
##/code-section module-header

schema = Schema((

    StringField(
        name='username',
        widget=StringWidget(
            label="Flickr Screenname",
            description="Not necessarily the same thing as your username, check your screenname by visiting your flickr account",
            label_msgid='flickrgallery_label_username',
            description_msgid='flickrgallery_help_username',
            i18n_domain='flickrgallery',
        )
    ),
    StringField( 
       name='group', 
       widget=StringWidget( 
           label="Group", 
           description="Flickr group NSID (e.g. 31939107@N00), used to Retrieve pictures from a group, leave this blank to retrieve pictures by the username above", 
           label_msgid='flickrgallery_label_username', 
           description_msgid='flickrgallery_help_username', 
           i18n_domain='flickrgallery', 
      ) 
   ), 

DataGridField(
        name='categories',
        columns=('category','tags'),
        widget=DataGridField._properties['widget'](
            columns={ 'category' : Column("Category"), 'tags':Column("Tags") },
            label='Categories',
            description_msgid='flickrgallery_help_categories',
            label_msgid='flickrgallery_label_categories',
            i18n_domain='flickrgallery',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here

##/code-section after-local-schema

FlickrGallery_schema = ATDocumentSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
FlickrGallery_schema['text'].widget.visible = {'view':'invisible','edit':'invisible'}
FlickrGallery_schema['text'].required = False
##/code-section after-schema

class FlickrGallery(ATDocument):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATDocument,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'FlickrGallery'

    meta_type = 'FlickrGallery'
    portal_type = 'FlickrGallery'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 1
    content_icon = 'flickrgallery.png'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "FlickrGallery"
    typeDescMsgId = 'description_edit_flickrgallery'

    _at_rename_after_creation = True

    schema = FlickrGallery_schema

    ##code-section class-header #fill in your manual code here
    default_view = 'flickrgallery_view'
    ##/code-section class-header

    # Methods

    security.declarePublic('showpictures')
    def showpictures(self, tags="",page='1',per_page='100',category="",text=''):
        """
        """
        username = self.getUsername()
        group = self.getGroup()
        tags=self.get_tags_by_category(category)
        

        FlickrAgent = flickrengine.FlickrAgent(username)
        if len(group) > 0:
            return FlickrAgent.showphotos(group=group,tags=tags,page=page,per_page=per_page,text=text)
        else:
            return FlickrAgent.showphotos(tags=tags,page=page,per_page=per_page,text=text)

    security.declarePublic('getpic_info')
    def getpic_info(self, photo_id=""):
        """
        """
        username = self.getUsername()
        FlickrAgent = flickrengine.FlickrAgent(username)
        pic_info = FlickrAgent.getinfo(photo_id)
        return pic_info

    security.declarePublic('getcategories')
    def getcategories(self):
        """
        """
        categories = self.getCategories()
        return categories

    security.declarePublic('generate_url')
    def generate_url(self, photo_id="", size="", download="false"):
        """
           generates the url for the flickr image
        """
        username = self.getUsername()
        FlickrAgent = flickrengine.FlickrAgent(username)
        pic_url = FlickrAgent.generate_url(photo_id=photo_id, size=size, download=download)
        return pic_url

    security.declarePublic('gen_size_url')
    def gen_size_url(self, photourl="", size=""):
        """
          generates the url for downloading the flickr image
        """
        i = photourl.rindex('.')
        temp = [photourl[:i],  photourl[i:] ] 
        if size == "sq":
            newsize =  "_s";    
        elif size == "t":
            newsize =  "_t";    
        elif size == "s":
            newsize =  "_s";    
        elif size == "m":
            newsize =  "_m";    
        elif size == "l":
            newsize =  "_l";    
         
        pic_url = temp[0] + newsize + temp[1]
        return pic_url

    
    security.declarePublic('getsizes')
    def getsizes(self, photo_id=""):
       """
          returns the available photo sizes   
       """
       username = self.getUsername()
       FlickrAgent = flickrengine.FlickrAgent(username)
       sizes = FlickrAgent.getsizes(photo_id)

       return sizes

    security.declarePublic('gen_download_url')
    def gen_download_url(self, photourl=""):
        """
          generates the url for downloading the flickr image
        """
        i = photourl.rindex('.')
        temp = [photourl[:i],  photourl[i:] ] 
        pic_url = temp[0] + "_d" + temp[1]
        return pic_url

    security.declarePublic('get_tags_by_category')
    def get_tags_by_category(self,category):
        """
        accepts a category and returns the list of tags
        """
        category_tuple = self.getcategories()
        tags = [category_dict['tags'] for category_dict in category_tuple if category_dict['category'] == category]
        try:
            tags = tags[0] 
        except IndexError:
            tags = '' 
        return tags



registerType(FlickrGallery, PROJECTNAME)
# end of class FlickrGallery

##code-section module-footer #fill in your manual code here
##/code-section module-footer



