#!/usr/bin/env python
# encoding=utf-8
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

import argparse
from controllers.http_links_collector import HttpLinksCollector
import logging
import json

class RicardoCrawler:
    '''RicardoCrawler class to crawl a web using system parameters.

    Created on 27/09/2012

    @author: Ricardo García Fernández
    @mail: ricardogarfe@gmail.com
    
    '''
    
    def __init__(self):
        '''Init method
        '''
        self.setup_log()
        self.crawler_start()

    def crawler_start(self):
        '''Method to start crawling.
            * Checks input parameters.
            * returns the result of crawling printing a dictionary on the screen.
        
        '''

        # ArgParse definition rules
        parser = argparse.ArgumentParser(description="Let's crawl a web")
        
        parser.add_argument('url', nargs=1, help='target URL')
        parser.add_argument('-n', '--number-of-levels', type = int, \
                            default = 1, help = 'how depth the crawl will go.')
        
        # Create argument object
        args = parser.parse_args()
        
        target_url = args.url.pop()
        depth = args.number_of_levels
        
        # Starting level to retrieve links
        level = 1
        links = {}
        http_links_collector = HttpLinksCollector(target_url)
        
        links_list = http_links_collector.\
            retrieve_links(target_url, depth, level)
        
        links[target_url] = links_list
        
        links_result = json.dumps(links, sort_keys=True, indent=4)

        # Print result in json view mode.
        self.logger.info(links_result)

    def setup_log(self):
        '''Setup Python logging.
        
        '''

        self.logger = logging.getLogger('ricardo-crawler')
        self.hdlr = logging.FileHandler('/var/tmp/crawler.log')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s \
            %(filename)s %(message)s')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(logging.INFO)


def main():
    '''Main method to initialize project.
    '''

    RicardoCrawler()

if __name__ == '__main__':
    main()     
