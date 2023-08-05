# coding=UTF-8
'''
    This file is part of crawler-mswl.

    crawler-mswl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    crawler-mswl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with crawler-mswl.  If not, see <http://www.gnu.org/licenses/>.

'''

class ScrapItem:
    ''' Define here the models for your scraped items.
    
    Created on 08/10/2012

    @author: Ricardo García Fernández
    @mail: ricardogarfe@gmail.com

    '''

    def __init__(self, title="", description="", links={}):
        self.title = title
        self.description = description
        self.links = links

    def set_title (self, title):
        ''' Set title value.
        
        '''

        if title:
            self.title = title
        
        pass

    def set_description (self, description):
        ''' Set description value.
        
        '''
        
        if description:
            self.description = description
        
        pass

    def set_links (self, links):
        ''' Set links value.
        
        '''

        if links:
            self.links = links
        
        pass
    
    def get_title(self):
        ''' Returns title value.
        
        '''
        
        return self.title
    
    def get_description(self):
        ''' Returns description value.
        
        '''
        
        return self.description
    
    def get_links(self):
        ''' Returns links value.
        
        '''
        
        return self.links
