import re
from datetime import datetime
from httplib import *
from jinja2 import *
from hpppm.error_handler import *

__version__ = '0.1'

class DemandManagement(ErrorHandler):
    """ 
        A framework that helps automate the Web service interaction offered by
        HP Project and Portfolio Management(aka - HPPPM).HPPPM is an industry
        wide tool that is used to standardize, manage and capture the execution
        of a project and operational activities.For more on HPPPM refer the 
        online documentation at HP.HPPPM offers Web Service operations to 
        various interfacing applications involved in a project to talk to each
        other.HPPPM offers solutions for various activities of an organization
        viz - application portfolio, demand, financial and so on.This framework
        currently supports Demand Management only.

        The framework is built up on 3 modules that have a designated task to do:
        field_parser  - A Higher Order Python parser meant to parse the input fields 
                        that will be used in creating the Web service request.
                        This module is generic and can be used by others after 
                        tweaking as per need.
        error_handler - Performs command line parsing, validation and error/info 
                        extraction.
        demand_management - Creates the Web Service request and does an HTTP post 
                            to the Web service.
 
        All the above modules offer utilities/methods/functions to the outside 
        world.The framework is typically meant to run via a wrapper script that
        uses the utilities offered.A sample wrapper script is bundled along with 
        this distribution under the bin dir. 

        SYNOPSIS:

        Command Call:
 
        python bin/hpppm_demand_management.py -o createRequest -u user -p password -f data/createRequest.data -c cfg/logging.conf

        -o is the webservice operation being performed
        -u user authorized to perform web service operation
        -p user's password
        -f location of file containing input fields that will be used to create
           the web service request.Instead of a path this can also be a string
           containing the input fields.A sample data file for each web service
           operation has been bundled along with distribution under data dir.  
        -c location to the configuration file that drives logging behavior.


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
                        
        DETAILS:

        A little knowledge in how HPPPM works is absolutely necessary if you 
        intend to use this framework to automate webservice calling for you.
        In HPPPM each work item is designated as a request and is similar in
        concept to a ticket in many ticketing systems.
        A request in HPPPM is made up of request type, request header type 
        and workflow.The request type and header are made up of request fields,
        validations, rules, security and statuses.The workflow is the request
        component that gets activated once the request is submitted.The workflow
        is made up various sub components that are classified as Executional, 
        Decisional, Conditional and SubWorkflows.The Decisional subcompnents 
        are the trigger points for user action and they in turn trigger the
        Executional and/or Conditional sub components as governed by the 
        business logic.Please note that all fields have a unique token name
        through which it is referenced internally and also in the Webservice
        call.
 
        Following are the Web Service Operations that the framework helps you 
        play with:

        addRequestNotes - Add notes to an existing PPM request.
        createRequest   - Create a new request in PPM.
        deleteRequest   - Delete PPM requests.
        executeWFTransitions - Move workflow and the request as a whole from
                               one Decision step to another.
        getRequests     - Get PPM request fields and their values.
        setRequestFields - Update fields of an existing PPM request.
        setRequestRemoteReferenceStatus - Updates the status of a remote 
                                          reference in a request in PPM.

        example:

        Let us assume that application XYZ wants to create a HP PPM request 
        using this framework.XYZ application will need the following(apart 
        from this framework installed and working)

        username of the user authorized in PPM to do the webservice operation
        password of the above user in PPM 
        input fields in the format the framework expects

        A sample input field format:
   
        "<serviceUrl>" "http://abc.com:8080/ppmservices/DemandService?wsdl" "</serviceUrl>" "<requestType>" "ABC" "</requestType>" "<fields>" "REQ.VP.APPLICATION" "COMMON" "REQ.VP.ID" "1102" "REQD.VP.RELATED" "No" "REQ.VP.PRIORITY" "2" "</fields>" "<URLReferences>" "abc" "abc" "abc" "</URLReferences>" "<notes>" "varun" "test by varun" "</notes>"

        All token names and their values go inside the <fields> tags.If you are
        setting URLReferences they must atleast have a single field which is the
        name("abc" above) of the URLReference that will appear in the PPM request.
        For notes write the authorname first followed by the note.Enclose all tags
        ,fields and their values in double quotes and separated by spaces.

        The XYZ application needs to change the input fields as per their requirement
        and use the command call listed in SYNOPSIS to create a request in the PPM 
        environment enclosed between serviceUrl tag.

        Following is a listing of supported Web services operations and their 
        mandatory input types:

        createRequest                   : serviceUrl, requestType, fields
        addRequestNotes                 : serviceUrl, requestId, notes
        executeWFTransitions            : serviceUrl, receiver, transition
        deleteRequests 			: serviceUrl, requestIds
        getRequests  			: serviceUrl, requestIds
        setRequestFields 		: serviceUrl, requestId, fields
        setRequestRemoteReferenceStatus : serviceUrl, receiver, source, status, fields
       
        Following is the sample input for various operations supported by this 
        framework:

        addRequestNotes:
        "<serviceUrl>" "http://abc.com:8080/ppmservices/DemandService?wsdl" "</serviceUrl>" "<requestId>" "30990" "</requestId>" "<notes>" "varun" "test by varun" "</notes>"

        deleteRequests:
        "<serviceUrl>" "http://abc.com:8080/ppmservices/DemandService?wsdl" "</serviceUrl>" "<requestIds>" "31520" "31521" "</requestIds>"

        executeWFTransitions:
        "<serviceUrl>" "http://abc.com:8080/ppmservices/DemandService?wsdl" "</serviceUrl>" "<receiver>" "31490" "</receiver>" "<transition>" "Review Complete" "</transition>"

        getRequests:
        "<serviceUrl>" "http://abc.com:8080/ppmservices/DemandService?wsdl" "</serviceUrl>" "<requestIds>" "30935" "30936" "</requestIds>"

        setRequestFields:
        "<serviceUrl>" "http://abc.com:8080/ppmservices/DemandService?wsdl" "</serviceUrl>" "<requestId>" "31490" "</requestId>" "<fields>" "REQD.VP.ORG" "ABC" "REQD.VP.DETAILED_DESC" "Test by Varun" "</fields>"

        setRequestRemoteReferenceStatus:
        "<serviceUrl>" "http://abc.com:8080/ppmservices/DemandService?wsdl" "</serviceUrl>" "<receiver>" "31490" "http://t.com:8090" "</receiver>" "<source>" "31490" "http://t.com:8090" "</source>" "<status>" "Assigned" "</status>" "<fields>" "REQD.VP.ORG" "Another test" "REQD.VP.DETAILED_DESC" "Another test Varun" "</fields>"
        
        For reference sake the above sample inputs for various operations is also
        saved under data dir.

        LOGGING & DEBUGGING:
        To enable troubleshooting the framework logs activites in a log file(
        sample stored under logs dir).The logging is controlled via a config
        file stored under cfg dir.
  
        A VERY IMPORTANT NOTE:
        The framework supports test driven development and has a test suite
        to help in unit testing.The test suite can be located under the test
        dir.Also, before using this framework take a look at the various
        templates under the templates directory and modify them as per your
        specifications.This framework works for HPPPM 9.14 and is backward 
        compatiable as well.However, if you come across any deviations please
        feel free to mail me your observations.
         
    """   

    def create_request(self, inputs):
        """ Create request from inputs passed using templates """

        logger    = logging.getLogger(__name__)
        operation = self.data['CURRENT_OPERATION']
        self.data['DATETIME'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z")

        logger.info("Creating Request for "+operation+" operation")

        try:
            env = Environment(loader=PackageLoader('hpppm', 'templates'))
            template = env.get_template(operation+'.xml')
            inputs.update(self.data)
            request = template.render(inputs)
        except TemplateNotFound, err:
            logger.error("Req creation failed Error: "+str(err)+" not found")
            sys.exit(1)
        except UndefinedError, err:
            logger.error("Req creation failed Error: "+str(err)+" not defined")
            sys.exit(1)
        except TemplateSyntaxError, err:
            logger.error("Req creation failed Error: "+str(err)+" syntax error")
            sys.exit(1)

        logger.info("Request created successfully!")
        logger.debug("Request created:\n"+request)

        return request

    def post_request(self, url, request, host=None, port=None):
        """ POSTs the request to the url passed in.Tries to extract the host 
            and port from the url if host and port are not passed in.Checks if
            the web service url is available before posting the request.
        """

        logger     = logging.getLogger(__name__)
        operation  = self.data['CURRENT_OPERATION']

        if not self.check_url_availability(url): return False

        if not (host and port):
            match      = re.search(r'://(?P<host>.+?):(?P<port>\d+)/', url)
            host, port = match.group('host'), match.group('port')

        logger.info("About to POST above request to "+url)

        try:       
            http       = HTTPConnection(host, port)
            http.request("POST", url, body=request, headers = {
                         "SOAPAction": operation,
                         "Content-Type": "text/xml; charset=UTF-8",
                         "Content-Length": len(request)
            })
            response = http.getresponse().read()
        except HTTPException, err:
            logger.error("Posting failed Error: "+str(err))
            sys.exit(1)

        logger.info("POSTing successful!")
        logger.debug("Response received:\n"+response)
        
        return response

    
if __name__ == '__main__':
    pass
