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

import urllib2
import logging
from BeautifulSoup import BeautifulSoup as Soup
from urllib2 import HTTPError, URLError
import traceback
from httplib import BadStatusLine

class UrlContentRetrieve:
    '''Controller class to manage url and retrieve content using BeautifulSoup.

    Created on 27/09/2012

    @author: Ricardo García Fernández
    @mail: ricardogarfe@gmail.com

    '''

    def __init__(self, top_url):
        '''Initializes UrlContentRetrieve with default user_agent.
        
        Keyword arguments:
        top_url -- URL from top web level.
        
        '''
        
        # Setup Log
        self.setup_log()

        # Define user agent
        user_agent = "Mozilla/5.0 (X11; U; Linux x86_64; en-Us) \
            AppleWebKit/534.7 (KHTML, Like Gecko) Chrome \
            /7.0.517.41 Safari/534.7"

        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('User-agent', user_agent)]
        
        if top_url.endswith("/"):
            self.top_url = top_url[:-1]
        self.top_url = top_url

    def url_content(self, target_url):
        ''' Retrieve URL raw Content.
        
        Keyword arguments:
        target_url -- url to inspect.
        
        '''
        
        # Get correct format of URL
        target_url = self.generate_correct_url(target_url)

        try:
            raw_code = self.opener.open(target_url)
            soup_code = Soup(raw_code, fromEncoding="utf-8")
        except HTTPError, http_error:
            self.logger.error("HttpError with url:\t" + target_url + \
                              "\nException message:\t " + \
                                str(http_error)\
                                + "\nStack trace:\t" + \
                                traceback.format_exc())
            return None
        except URLError, url_error:
            self.logger.error("URLError with url:\t" + target_url + \
                              "\nException message:\t " + \
                                str(url_error)\
                                + "\nStack trace:\t" + \
                                traceback.format_exc())
            return None
        except BadStatusLine, bad_status:
            self.logger.error("BadStatusLine with url:\t" + target_url + \
                              "\nException message:\t " + \
                                str(bad_status)\
                                + "\nStack trace:\t" + \
                                traceback.format_exc())
            return None
        except Exception, exception:
            self.logger.error("Exception with url:\t" + target_url + \
                              "\nException message:\t " + \
                                str(exception)\
                                + "\nStack trace:\t" + \
                                traceback.format_exc())
            return None
            
        return soup_code

    def generate_correct_url(self, url_to_check):
        ''' Check the url and generate a new one well formed if is not complete.
            * Url management starts with '/' or /wiki/ - InvalidURL
            * Url management starts with '//' - HTTPError
            * Url format t0 utf-8 - http://es.wikipedia.org//yi.wikipedia.org/wiki/%D7%B0%D7%99%D7%A7%D7%99%D7%A4%D6%BC%D7%A2%D7%93%D7%99%D7%A2:%D7%91%D7%A8%D7%95%D7%9B%D7%99%D7%9D_%D7%94%D7%91%D7%90%D7%99%D7%9D
        
        Keyword arguments:
        url_to_check -- URL to check

        '''

        try:
            url_to_check = str(url_to_check.encode('utf-8'))
        except UnicodeEncodeError, unicode_error:
            self.logger.warning("UnicodeEncodeError with url:\t" + \
                              url_to_check + "\nException message:\t " + \
                                str(unicode_error)\
                                + "\nStack trace:\t" + \
                                traceback.format_exc())
            return None

        if url_to_check.startswith("//"):
            url_to_check = "http:" + url_to_check
        elif url_to_check.startswith("/"):
            url_to_check = self.top_url + url_to_check
        elif url_to_check.startswith("#"):
            url_to_check = None
        elif not url_to_check.find("https://") and \
            not url_to_check.find("http://"):
            url_to_check = self.top_url + url_to_check

        return url_to_check

    def retrieve_formatted_links(self, soup_code):
        ''' Retrieve the links in correct format into a list.
        
        '''

        formatted_links = []
        raw_links = []

        # Extract all links
        for link in soup_code.findAll('a') :
            if link.has_key('href'):
                raw_links.append(link['href'])
        
        # Convert to correct format
        for raw_link in raw_links:
            formatted_link = self.generate_correct_url(raw_link)
            if formatted_link:
                formatted_links.append(formatted_link)
            
        return formatted_links

    def setup_log(self):
        '''Setup Python logging.
        
        '''

        self.logger = logging.getLogger('UrlContentRetrieve')
        self.hdlr = logging.FileHandler('/var/tmp/crawler.log')
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s \
            %(filename)s %(message)s')
        self.hdlr.setFormatter(self.formatter)
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(logging.WARNING)
