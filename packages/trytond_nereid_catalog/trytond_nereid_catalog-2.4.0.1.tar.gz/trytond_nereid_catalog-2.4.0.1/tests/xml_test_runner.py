# -*- coding: utf-8 -*-
'''
    Catalog XML Test runner
    
    :copyright: (c) 2010-2012 by Openlabs Technologies & Consulting (P) Ltd.
    :license: GPLv3, see LICENSE for more details
    
'''
from nereid.contrib.testing import xmlrunner
from test_catalog import suite

if __name__ == '__main__':
    with open('result.xml', 'wb') as stream:
        xmlrunner.XMLTestRunner(stream).run(suite())
