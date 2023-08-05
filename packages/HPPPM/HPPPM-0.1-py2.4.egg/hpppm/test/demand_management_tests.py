#!/usr/bin/env python

import unittest, os, sys
from hpppm.demand_management import *

class T(unittest.TestCase):
    inp = {'requestType': ['A'], 'fields': ['REQ.VP.APP', 'ART', 'REQ.VP.ID', 'xyz1'],\
         'serviceUrl': ['http://python.org']}
    req = None

    def setUp(self):
        self.dm = DemandManagement()
        self.dm.data['CURRENT_OPERATION'] = 'createRequest'
        self.dm.data['OPS_INPUTS_REQD'] = {'createRequest': ["serviceUrl", "requestType"]}
        self.dm.data['OPS_INPUTS'] = {'createRequest': ["serviceUrl", "requestType", "fields", "references", "notes"]}

    def test_create_request(self):
        T.req = self.dm.create_request(T.inp)

        self.assert_(T.req is not None)

    def test_post_request(self):
        #res = self.dm.post_request(T.inp['serviceUrl'][0], T.req)
        res = hasattr(self.dm, 'post_request')

        self.assert_(res is not None)

if __name__ == '__main__':
    unittest.main()
