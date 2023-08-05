#!/usr/bin/python
import hpppm.field_parser
from hpppm.demand_management import *

if __name__ == '__main__':
    """ Replace with actual documentation   """

    hpdm = DemandManagement();

    fields = hpdm.validate_read_cmdargs(sys.argv)
    tags   = hpdm.get_inputs(hpdm.get_current_oper())
    inputs = hpppm.field_parser.parser(fields, tags)
    ret    = hpdm.validate_inputs(inputs)
    if 'fields' in tags: ret = hpdm.validate_tokens(inputs['fields'])

    req = hpdm.create_request(inputs)
    res = hpdm.post_request(inputs['serviceUrl'][0], req)
    ret = hpdm.extract(res, to_extract=['faultcode', 'faultstring',\
                                         'exception:detail', 'id', 'return'])

    print res 

