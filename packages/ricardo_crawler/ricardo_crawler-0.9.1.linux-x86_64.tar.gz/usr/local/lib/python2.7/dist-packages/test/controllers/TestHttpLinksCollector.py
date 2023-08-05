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

import unittest
from controllers.http_links_collector import HttpLinksCollector

class TestHttpLinksCollector (unittest.TestCase):
    '''Test class for methods defined in HttpLinksCollector class.
    
    Created on 01/10/2012

    @author: Ricardo García Fernández
    @mail: ricardogarfe@gmail.com

    '''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_retrieveLinks(self):
        '''Test method for HttpLinksCollector.retrieve_links.
        
        '''
        
        # Test 1 - check HttpError 401 in log
        starting_url = "http://www.nature.com"
        target_url = "http://www.nature.com/nature/journal/v438/n7070/full/438900a.html"

        http_links_collector = HttpLinksCollector(starting_url)        
        links_retrieved = http_links_collector.retrieve_links(target_url)
        
        self.assertTrue(not links_retrieved, \
                       "Retreved Links from:'" + target_url + "'")
        
        # Test 2 - check URLError - protocol irc.
        starting_url = "http://www.nature.com"
        target_url = "irc://irc.freenode.net/wikimedia-ayuda"

        http_links_collector = HttpLinksCollector(starting_url)        
        links_retrieved = http_links_collector.retrieve_links(target_url)
        
        self.assertTrue(not links_retrieved, \
                       "Retreved Links from:'" + target_url + "'")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testRetrieveLinks']
    unittest.main()
