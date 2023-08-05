#!/usr/bin/env python

import unittest, os, sys, re
from hpppm.error_handler import *
import hpppm.field_parser

class T(unittest.TestCase):
    i  = {}
    f  = '"<serviceUrl>" "http://docs.python.org" "</serviceUrl>" '
    f += '"<requestType>" "ABC" "</requestType>" '
    f += '"<fields>" "REQ.VP.APPLICATION" "TT" "REQ.VP.UID" "111" "</fields>" '
    f += '"<references>"  "URL" "http://abc.com/uploads/03-May-12_080901/wb.txt" "</references>" '
    f += '"<notes>" "author" "Additional Info" "</notes>"'
    a = ['scriptname', '-o', 'createRequest', '-u', 'user', '-p', 'pass', '-f', f, '-c', 'cfg/logging.conf']

    def setUp(self):
        self.eh = ErrorHandler()
        self.eh.data  = {}
        self.eh.data['CURRENT_OPERATION'] = 'createRequest'
        self.eh.data['OPS_INPUTS_REQD'] = {'createRequest': ["serviceUrl", "requestType"]}
        self.eh.data['OPS_INPUTS'] = {'createRequest': ["serviceUrl", "requestType", "fields", "references", "notes"]}

    def test_validate_read_cmdargs(self):
        T.f = self.eh.validate_read_cmdargs(T.a)

	self.assert_(T.f is not None)

    def test_validate_inputs(self):
        tags = self.eh.get_inputs('createRequest')
        T.i  = hpppm.field_parser.parser(T.f, tags)
        ret  = self.eh.validate_inputs(T.i)

	self.assertEqual(ret, True)

    def test_validate_tokens(self):
        ret = self.eh.validate_tokens(T.i['fields'])

	self.assertEqual(ret, True)

    def test_check_url_availability(self):
        url = "http://mail.yahoo.com"

	ret = self.eh.check_url_availability(url)

	self.assertEqual(ret, True)

    def test_extract(self):
        resp = '<?xml version=\'1.0\' encoding=\'UTF-8\'?><soapenv:Envelope xmlns:soapenv='
        resp += '"http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Header /><soapenv:Fault>'
        resp += '<faultcode>UNKNOWN</faultcode><faultstring>GUID</faultstring>'
        resp += '</soapenv:Fault></soapenv:Envelope>'

	ret = self.eh.extract(resp, ['faultcode', 'faultstring'])

	self.assert_('faultcode' or 'faultstring' in ret)

if __name__ == '__main__':
    unittest.main()
