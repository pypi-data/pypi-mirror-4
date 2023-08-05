import re
import sys
import string
import mechanize
import getopt
import logging
import logging.config
import os.path as op

#for the time being
#from lxml import etree

__version__ = '0.1'

class ErrorHandler:

    def __init__(self):
        self.data  = {}
        self.__set_ops_inputs_reqd()
        self.__set_ops_inputs()


    def __set_ops_inputs_reqd(self):
        """Stores the mapping between operation and the mandatory inputs/types.
	   For e.x. "createRequest" operation needs atleast the "requestType"
	   type to be present in the input fields.
	"""

	self.data["OPS_INPUTS_REQD"] = { \
	    #operations                      > Mandatory inputs/types
	    'createRequest'        : ["serviceUrl", "requestType", "fields"],\
	    'addRequestNotes'      : ["serviceUrl", "requestId", "notes"],\
	    'executeWFTransitions' : ["serviceUrl", "receiver", "transition"],\
	    'deleteRequests'       : ["serviceUrl", "requestIds"],\
	    'getRequests'          : ["serviceUrl", "requestIds"],\
	    'setRequestFields'     : ["serviceUrl", "requestId", "fields"],\
	    'setRequestRemoteReferenceStatus': ["serviceUrl", "receiver",\
                                                "source", "status", "fields"],\
        }

    def __set_ops_inputs(self):
        """Stores the mapping between operation and inputs/types.
	"""

	self.data["OPS_INPUTS"] = { \
	    'createRequest'        : ["serviceUrl", "requestType",\
                                      "fields", "URLReferences", "notes"],\
	    'addRequestNotes'      : ["serviceUrl", "requestId", "notes"],\
	    'executeWFTransitions' : ["serviceUrl", "receiver", "transition"],\
	    'deleteRequests'       : ["serviceUrl", "requestIds"],\
	    'getRequests'          : ["serviceUrl", "requestIds"],\
	    'setRequestFields'     : ["serviceUrl", "requestId", "fields"],\
	    'setRequestRemoteReferenceStatus': ["serviceUrl", "receiver",\
                                                "source", "status", "fields"],\
        }

    def get_supported_ops(self):
        """List supported operations"""

        return self.data["OPS_INPUTS_REQD"].keys()


    def get_current_oper(self):
        """List current operation"""

        return self.data["CURRENT_OPERATION"]


    def get_reqd_inputs(self, operation=None):
        """Lists must have types inorder to perform the operation.If operation
           is not passed or is None returns all the operations supported along
           with the mandatory types for each.
           for e.g. - for createRequest operation the input fields must have
                      requestType details.
	"""

        if operation: return self.data["OPS_INPUTS_REQD"][operation]
        else:         return self.data["OPS_INPUTS_REQD"]


    def get_inputs(self, operation=None):
        """Lists types inorder to perform the operation.If operation
           is not passed or is None returns all the operations supported along
           with the types for each.
	"""

        if operation: return self.data["OPS_INPUTS"][operation]
        else:         return self.data["OPS_INPUTS"]

   
    def __check_reqd_types(self, fields, reqd_types):
        """Checks if the input fields that will be used to construct the request
	   message have all the reqd. (per operation) types present.Both inputs
	   fields and the reqd types are mandatory inputs.Returns True
	   if the reqd. types are present.
	"""

	logger    = logging.getLogger(__name__)
	operation = self.data['CURRENT_OPERATION']

	def is_present(x): return fields[x]
	present_types = filter(is_present, reqd_types)

	if len(present_types) == len(reqd_types): return True

	reqd    = string.join(reqd_types, ",")
	present = string.join(present_types, ",")
	msg     = "Properties present don't match the min. no of "
	msg    += "properties needed for "+operation+".Properties "
	msg    += "present: "+present+" reqd: "+reqd+" Exiting!"

	logger.error(msg)
	sys.exit(1)

    def __get_file_content(self, fname):
        """ Read and return file contents as a single string """

        logger = logging.getLogger(__name__)

        try:
            logger.debug("About to read fields containing req fields")
            fhandle = open(fname,'r')
            fields  = fhandle.read().replace('\n', '')
        except IOError, err:
            print "Unable to read ",fname,"..Exiting!",str(err)
            logger.error("Unable to read "+fname+" "+str(err))
            sys.exit(1)
        else:
            logger.debug(fname+" "+"read! content:"+fields)
            fhandle.close()

        return fields


    def validate_read_cmdargs(self, cmdargs):
        """ 
            python bin/hpppm_demand_management.py -o createRequest -u user -p password -f data/createRequest.data -c cfg/logging.conf

            -o or --operation  is the webservice operation being performed
            -u or --user       user authorized to perform web service operation
            -p or --password   user's password
            -f or --fields     location of file containing input fields that will be used to create
                               the web service request.Instead of a path this can also be a string
                               containing the input fields.A sample data file for each web service
                               operation has been bundled along with distribution under data dir.
            -c or --logconfig  location to the configuration file that drives logging behavior.
            -h or --help or -? display help.

            Utilites and typical usage:

            import hpppm.field_parser
            from hpppm.demand_management import *

            hpdm = DemandManagement();

            fields = hpdm.validate_read_cmdargs(sys.argv)
            tags   = hpdm.get_inputs(hpdm.get_current_oper())
            inputs = hpppm.field_parser.parser(fields, tags)
            ret    = hpdm.validate_inputs(inputs)
            if 'fields' in tags: ret = hpdm.validate_tokens(inputs['fields'])

            req = hpdm.create_request(inputs)
            res = hpdm.post_request(inputs['serviceUrl'][0], req)
            ret = hpdm.extract(res, to_extract=['faultcode', 'faultstring', 'exception:detail', 'id', 'return'])
        """

        try:
            opts, args = getopt.getopt(cmdargs[1:], "h?o:u:p:f:c:",\
            ["help", "operation=", "user=", "password=", "fields=", "logconfig="])
        except getopt.GetoptError, err:
            print str(err), self.validate_read_cmdargs.__doc__
            sys.exit(2)

        oper, user, pasd, fields, logconf = None, None, None, None, None

        for o, a in opts:
            if o in ("-h", "--help", "-?"):
                print  self.validate_read_cmdargs.__doc__
                sys.exit(1)
            elif o in ("-o", "--operation"):
                oper, self.data['CURRENT_OPERATION'] = a, a
            elif o in ("-u", "--user"):
                user,self.data['USER'] = a, a
            elif o in ("-p", "--password"):
                pasd,self.data['PASSWORD'] = a, a
            elif o in ("-f", "--fields"):
                fields = a
            elif o in ("-c", "--logconfig"):
                logconf = a
            else:
                assert False, "Illegal/Unhandled Option"

        if (oper and user and pasd and fields and logconf) in (None, ' ', " "): 
            print "Insufficient Arguments.Exiting!", self.validate_read_cmdargs.__doc__
            sys.exit(1)

        if op.exists(logconf) is False or op.getsize(logconf) == 0:
            assert False,"Log config doesn't exist or size 0.Exiting!"

        logging.config.fileConfig(logconf)
        logger = logging.getLogger(__name__)

        if oper in self.get_supported_ops():
            logger.info("Current operation is "+oper)
        else:
            logger.error("Unsupported operation: "+oper)
	    sys.exit(1)

        #Check if fields is a file; if it is slurp content in fields
        if op.isfile(fields) and op.exists(fields) and op.getsize(fields):
            fields = self.__get_file_content(fields)
        else:
            logger.info(fields+' '+"Not a file proceeding ahead")

        return fields
 

    def validate_inputs(self, fields, ignore_types=[]):
        """ Checks if the required types need in order to perform the 
            operation successfully are present or not.
	"""

	logger          = logging.getLogger(__name__)
	operation       = self.data['CURRENT_OPERATION']
	ops_inputs_reqd = self.data['OPS_INPUTS_REQD']

        #match = re.search(r'(?P<url>\w+\:\/\/[^\<"]+)', fields)
        #if match is None:
	#    logger.error("No service url specified.Exiting!")
	#    sys.exit(1)
        #else: 
	#    self.data['SERVICE_URL'], url =\
	#        match.group('url'), match.group('url')

	#if self.check_url_availability(url):
	#    logger.debug("Service URL "+url+" Available!")
        
	#Lookup and localize reqd types needed to perform the operation
	reqd_types = ops_inputs_reqd[operation]
	if self.__check_reqd_types(fields, reqd_types):
	    logger.debug("Reqd. Types for Current Oper Present!")

        return True


    def validate_tokens(self, fields=[]):
        """ Checks if the operation being performed supports tokens or
	    not. If no tokens are needed the method returns 0.Performs
	    the following checks on tokens as well -All field tokens
	    must be all caps. Token prefixes (REQD, REQ, UD, T, VP, P)
	    must be one of the specified types.All tokens can contain
	    only alphanumeric characters and _ (underscore).Input is
	    input fields and output is Success or Failure.
	"""

	logger           = logging.getLogger(__name__)
	operation        = self.data['CURRENT_OPERATION']
	ops_inputs_reqd  = self.data['OPS_INPUTS_REQD']

        if not fields:
	    logger.info("No token tags in input fields!")
	    return True

        tokens = [token for i, token in enumerate(fields) if i%2 == 0]
	def is_ill_token(x): return not \
	    re.search(r"^((?:REQD|REQ|UD|T)\.?(?:VP|P)?\.[A-Z_0-9]+?)$", x)
        illegal_tokens = filter(is_ill_token, tokens)
	if illegal_tokens:
	    illegal = string.join(illegal_tokens, ",")
	    logger.error("Illegal Token names: "+illegal+" Exiting!")
	    sys.exit(1)

        return True


    def check_url_availability(self, url):
        """ Tests service URL for accessibility.Input is url to test
	    and returns Success or Failure.
	"""

	logger = logging.getLogger(__name__)

	try:
            br       = mechanize.Browser()
	    br.set_handle_robots(False)
	    response = br.open(url)
        except IOError, err:
	    logger.error(url+" Unavailable Error: "+str(err))
	    sys.exit(1)

        return True

    def extract(self, resp, to_extract):
        """ Extracts the value between to_extract tags present in resp.
            The return value is a dictionary with key as the to_extract
            element and value as its extracted value.
        """

	logger = logging.getLogger(__name__)
	#get rid of any thing before the <?XML tag
	#resp   = re.sub(r"^.+(\<\?xml.*)$", r"\1", resp)
	#resp, flags=re.IGNORECASE) # flags not in python2.4
        values = {}

        logger.debug("About to extract values of following tags: ",to_extract)

	try:
	    from lxml import etree

	    root = etree.XML(resp)

            for tag in to_extract:
                value = root.find(".//%s"%tag)
                if value is not None: values[tag] = value.text

        except ImportError, err:
	    logger.debug(\
	      "lxml.etree import failed!Trying with regexp"+str(err))
            for tag in to_extract:
                match = re.search("<%s>(.+)</%s>"%(tag, tag), resp)
	        if match: values[tag] = match.group(1)

        logger.debug("TAGS -> VALUES: ",values)

	return values
