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

from url_content_retrieve import UrlContentRetrieve
import logging
import traceback

class HttpLinksCollector:
    '''Class to manage links from url.
    
    Created on 27/09/2012

    @author: Ricardo García Fernández
    @mail: ricardogarfe@gmail.com

    '''

    def __init__(self, starting_url):
        '''Initialize to set urlContentRetrieve object with startingURL.
        
        Keyword arguments:
        starting_url -- URL to start crawling.

        '''

        # Setup Log
        self.setup_log()
        # Define url content retrieve to use
        self.url_content_retrieve = UrlContentRetrieve(starting_url)
    
    def retrieve_links(self, target_url, depth=1, level=1):
        '''
        Retrieve links from url content until defined depth organized in levels.
        
        Keyword arguments:
        target_url -- URL to analyze content and retrive links.
        depth -- Depth of links to analyze.
        level -- Level in which start to analyze.
        
        '''

        # Define ScrapItem to generate json file
        # scrap_item = ScrapItem()
        
        links = {}

        if depth >= level:

            soup_code = self.url_content_retrieve.url_content(target_url)
            
            if soup_code:
                formatted_links = \
                    self.url_content_retrieve.\
                        retrieve_formatted_links(soup_code)
                for link in formatted_links :
    
                        self.logger.info(self.print_depth(level) + " " + link)
    
                        try:
                            sublinks = \
                                self.retrieve_links(link, depth, level + 1)
                            links[link] = sublinks
                        except ValueError, value_error:
                            # Invalid URL
                            self.logger.error("URL is not correct:\t" + link + \
                                              "\nException:\t"\
                                               + str(value_error)\
                                               +"\nStack trace:\t"+\
                                               traceback.format_exc())
                            
        # TODO: Return a dictionary of ScrapItems 
        return links
    
    def print_depth(self, level):
        '''
        Creates the string with the '*' character serie appropriate to the deep.

        Keyword arguments:
        level -- level to print *
        '''

        deepLetter = ""
        for i in range(level):
            deepLetter = deepLetter + "*"
            
        return deepLetter

    def setup_log(self):
        '''Setup Python logging.
        
        '''

        self.logger = logging.getLogger('HttpLinksCollector')
        self.hdlr = logging.FileHandler('/var/tmp/crawler.log')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s \
            %(filename)s %(message)s')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(logging.WARNING)
