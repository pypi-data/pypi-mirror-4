#!/usr/local/bin/python2.7
""" Unit Tests


See LICENSE.txt for Licensing details
Copyright (c) <2013> <Samuel M. Smith>

"""
import sys
import os

import gevent
from gevent import monkey
monkey.patch_all()

import logging
import unittest

import ssl 

import emptoring


class EmptorTestCase(unittest.TestCase):
    def setUp(self):
        pass
        
    
    def tearDown(self):
        pass
    
    def testBasic(self):
        """ Basic functionality"""
        gevent.sleep(0)
        logger.debug("\nBasic Test")
        emptor = emptoring.Emptor(port='8084', prefix = "/test/where")
        reaped = emptor()
        self.assertTrue(reaped.startswith('Web app is located at'))
    
    def testReapXml(self):
        """ Reaping XML """
        logger.debug("\nReap Test")
        import lxml
        
        s = """ <html>
                <head>
                    <title>Example page</title>
                </head>
                <body>
                    <p>Moved to 
                        <a href="http://example.org/">example.org</a>
                    or 
                        <a href="http://example.com/">example.com</a>.
                    </p>
                </body>
            </html>
        """
        try:    
            root = lxml.etree.fromstring(s) #get root element
        except (SyntaxError, ) as ex:
            raise ContentEmptorError(msg = "Invalid 'content' not xml", 
                                        content = s)
        
        #walk tree here generating hierarchical dict of values, lists, dicts     
        reaped = emptoring.Emptor.walk(root, '')
        
        g = {'body': 
                   {'p': 
                        {'a': [
                            {'@href': 'http://example.org/', 'value': 'example.org'}, 
                            {'@href': 'http://example.com/', 'value': 'example.com'}
                           ]
                        }
                    }, 
             'head': 
                 {'title': 'Example page'}
            }
        self.assertEquals(reaped,g)    
         

def testSome():
    """ Unittest runner """
    tests = []
    tests.append('testBasic')
    tests.append('testReapXml')
    
    suite = unittest.TestSuite(map(EmptorTestCase, tests))    
    unittest.TextTestRunner(verbosity=2).run(suite) 
        
def testAll():
    """ Unittest runner """
    suite = unittest.TestLoader().loadTestsFromTestCase(EmptorTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)    

if __name__ == '__main__' and __package__ is None:
    """ To run these tests first run from command line the bottle app these
        tests access
        
        $ cd /Volumes/Gob/Data/Jive/Code/elbonia/libs/tests
        $ ./serving.py
      
      """
    logger = logging.getLogger(__name__) #name logger after module
    logger.setLevel(logging.DEBUG)
    
    basicConsoleHandler = logging.StreamHandler() #sys.stderr
    basicformatter = logging.Formatter('%(message)s') #standard format
    basicConsoleHandler.setFormatter(basicformatter)
    logger.addHandler(basicConsoleHandler)
    logger.propagate = False
    
    import bottle
    import testapp #import testapp module
    logger.info("Starting wsgi server %s on %s:%s." % ('gevent', 'localhost', '8084'))
    gevent.spawn(bottle.run, app=testapp.app, server='gevent', host='localhost', port='8084' )    
    gevent.sleep(0)
    #testAll() #run all unittests
    
    testSome()#only run some
    
    
    
    
    #while True: #sleep parent Greenlet so alther Greenlets and run
        #gevent.sleep(0)    