import urllib2, json, base64


def production():
    '''
    Sets the target to the production server.
    '''
    global _domain
    _domain = 'https://work.mobileworks.com/'

def sandbox():
    '''
    Sets the target to the sandbox server.
    '''
    global _domain
    _domain = 'https://sandbox.mobileworks.com/'

# setting the domain to the production server
_domain = None
sandbox()


_version = 2
def version( v = None ):
    global _version
    if v == None:
        return _version
    try:
        _version = int( v )
    except ValueError:
        raise Exception( 'Version must be an integer!' )


def _make_request( url, method = None, post_data = None ):
    """
    Creates and sends an HTTP request.
    """
    class Request( urllib2.Request ):
        """
        This class is an extension of urllib2.Request that allows requests other than GET/POST.
        """
        def __init__( self, url, data = None, headers = {}, origin_req_host = None, unverifiable = False, method = None ):
            """
            These parameters (except `method`) are the same as the parameters in the parent class `urllib2.Request`, which can be found here:
            http://docs.python.org/library/urllib2.html#urllib2.Request
            
            The `method` parameter was added to allow HTTP requests other than GET/POST.
            """
            self._method = method
            urllib2.Request.__init__( self, url, data, headers, origin_req_host, unverifiable )
        
        def get_method( self ):
            return self._method if self._method else urllib2.Request.get_method( self )
        
    credentials = _authenticate()
    req = Request( url, method = method, data = post_data, headers = {'Content-Type':'application/json'} )
    req.add_header( 'Authorization', 'Basic ' + credentials )
    
    try:
        response = urllib2.urlopen( req )
        headers = response.info().dict
        content = response.read()
        response.close()
        return headers, content
    except urllib2.HTTPError, e:
        if e.code >= 500:
            raise Exception( 'HTTP %d: A server error occured' % e.code )
        else:
            raise Exception( 'HTTP %d: %s' % ( e.code, e.read() ) )


# credentials of the user: base64.encodestring( username + ':' + password )[:-1]
_credentials = None

def _authenticate():
    '''
    This will authenticate the user if he is not already authenticated.
    '''
    global _credentials
    if not username or not password:
        raise Exception( 'Please provide a username and password.' )
    new_credentials = base64.encodestring( username + ':' + password )[:-1]
    if not _credentials or _credentials != new_credentials:
        _credentials = new_credentials
        try:
            PROFILE_PATH = 'api/v1/userprofile/'
            headers, content = _make_request(_domain + PROFILE_PATH)
            _store_credentials()
        except Exception, e:
            print e
            _credentials = None
            raise Exception( "Authentication failed! To reset your password, please go to 'https://work.mobileworks.com/accounts/password_reset/'" )
    return _credentials


username = None
password = None

_DEFAULT_CREDENTIALS_FILE = '.mobileworks_credentials'

def _load_credentials():
    global _credentials, username, password
    try:
        import os
        f = open( os.path.join( os.getenv( 'HOME' ), _DEFAULT_CREDENTIALS_FILE ) )
        _credentials = f.read()
        f.close()
        username, password = base64.decodestring( _credentials ).split( ':', 1 )
    except Exception, e:
#        raise Exception( "Couldn't load your credentials. This exception was raised: %s" % e )
        pass

def _store_credentials():
    global username, password
    credentials = base64.encodestring( username + ':' + password )[:-1]
    try:
        import os
        f = open( os.path.join( os.getenv( 'HOME' ), _DEFAULT_CREDENTIALS_FILE ), 'w' )
        f.write( credentials )
        f.close()
    except Exception, e:
        print "Failed to store your credentials. This exception was raised: %s" % e

_load_credentials()

class _API:
    """
    This is the base class for Task/Job.
    It contains the general methods for making API calls to MobileWorks
    """
    
    location = None
    params = {}
    fields = None
    
    def __init__( self, **task_params ):
        self.params = task_params
    
    def get_param( self, name ):
        """
        Gets the specified parameter.
        """
        return self.params[name]
        
    def set_params( self, **params ):
        """
        Updates the parameters with whatever is specified by the keyword arguments.
        """
        self.params.update( params )
    
    def url( self ):
        return _domain + self._path()
    
    def dict( self ):
        """
        This is used for json serialization.
        It should be overriden by subclasses.
        """
        return self.__dict__
    
    def from_dict( self, dic ):
        self.params = dic
    
    def to_json(self):
        return json.dumps( self.dict() )
    
    def from_json(self, JSON):
        self.from_dict( json.loads( JSON ) )
    
    def __str__(self):
        return self.to_json()
    
    def add_field( self, name, type, **kwargs ):
        """
        Adds a field to this instance.
        """
        if _version < 2:
            raise Exception( "Fields only exist in version 2 of the API" )
        
        if not self.fields:
            self.fields = []
            
        field = {name: type}
        if kwargs:
            field.update( kwargs )
        self.fields.append( field )
    
    def post( self ):
        """
        Posts the object to MobileWorks API and returns the URL of the created object.
        """
        headers, content = _make_request( self.url(), 'POST', self.to_json() )
        if _version == 1:
            self.location = headers['location']
        elif _version == 2:
            self.location = json.loads(content)['Location']
        return self.location
    
    @classmethod
    def retrieve( cls, location ):
        """
        Gets the information of the object located at `location`.
        `location` can also be the object that was posted to MobileWorks.
        """
        try:
            # `location` is the object posted to MobileWorks
            url = location.location
        except:
            # `location` is just a url
            url = location
        headers, content = _make_request( url )
        new_obj = cls()
        new_obj.location = url
        new_obj.from_json( content )
        return new_obj
    
    def delete( self ):
        """
        Deletes the object located at `url`.
        """
        if self.location is None:
            raise Exception( "This object doesn't point to any resource on the server." )
        headers, content = _make_request( self.location, 'DELETE' )
        if _version == 1:
            return True
        elif _version == 2:
            return json.loads( content )
    

class Task(_API):
    
    def _path( self ):
        """
        Returns the base path of tasks depending on the API version.
        """
        if _version == 1:
            return 'api/v1/tasks/'
        elif _version == 2:
            return 'api/v2/task/'
        raise Exception( 'Sorry, version %d is not supported by the library yet!' % _version )
        
    def dict( self ):
        dic = self.params.copy()
        if self.fields is not None:
            dic.update( {'fields': self.fields} )
        return dic
        
    
    def _getResponsesUrl(self):
        return self.location.replace( '/task/', '/response/' )
    
    def getResponses(self):
        """
        Returns a list of response objects.
        """
        headers, content = _make_request( self._getResponsesUrl() )
        data = json.loads( content )
        responses = data['results']
        return [Response(self, r) for r in responses]
    
    def _getDecisionUrl(self, approve):
        """
        Gets the url for taking a decision on this task.
        """
        suffix = 'approve/' if approve else 'reject/'
        return self.location + suffix

    def _takeDecision(self, approve, reason):
        """
        Takes an approval/rejection decision on this task.
        It return True if the decision was accepted successfully.
        """
        if self.location is None:
            raise Exception( "This object doesn't point to any resource on the server." )
        
        url = self._getDecisionUrl( approve )
        postJson = json.dumps({'reason': reason})
        headers, content = _make_request( url, 'POST', postJson )
        parsedContent = json.loads( content )
        # if the decision fails, throw an exception
        if not parsedContent['success']:
            raise Exception( parsedContent.get( 'error', "Failed: server didn't provide any failure info." ) )
        return True

    def approve(self, reason = None):
        """
        Approve this task (this approves all results of this task).
        """
        return self._takeDecision( True, reason )

    def reject(self, reason = None):
        """
        Reject this task (this rejects all results of this task).
        """
        return self._takeDecision( False, reason )
    
    
class Job(_API):
    
    def __init__( self, **job_params ):
        self.params = job_params
        self.tasks = []
        self.test_tasks = None
        
    def _path( self ):
        """
        Returns the base path of jobs depending on the API version.
        """
        if _version == 1:
            return 'api/v1/job/'
        elif _version == 2:
            return 'api/v2/job/'
        raise Exception( 'Sorry, version %d is not supported by the library yet!' % _version )
        
    def add_task( self, task ):
        """
        Adds a task to this job.
        """
        try:
            task.dict
            self.tasks.append( task )
        except AttributeError:
            raise ValueError( "`task` must be a valid task object" )
        
    def add_test_task( self, test_task ):
        """
        Adds a test task to this job.
        """
        try:
            test_task.dict
            if not self.test_tasks:
                self.test_tasks = []
            self.test_tasks.append( test_task )
        except AttributeError:
            raise ValueError( "`test_task` must be a valid task object" )
    
    def dict( self ):
        dic = self.params.copy()
        if self.fields is not None:
            dic.update( {'fields': self.fields} )
        if self.tasks is not None:
            tasks = self.tasks
            if len( tasks ) and tasks[0].__class__ == Task:
                tasks = [t.dict() for t in tasks]
            dic.update( {'tasks': tasks} )
        if self.test_tasks is not None:
            tasks = self.test_tasks
            if len( tasks ) and tasks[0].__class__ == Task:
                tasks = [t.dict() for t in tasks]
            dic.update( {'tests': tasks} )
        return dic
    
    def from_dict( self, dic ):
        local_dic = dic.copy()
        if 'tasks' in local_dic:
            for task in local_dic['tasks']:
                new_task = Task()
                new_task.from_dict( task )
                self.tasks.append( new_task )
            del local_dic['tasks']
            self.params = local_dic
        
    

class Project(Job):
    
    def _path( self ):
        """
        Returns the base path of projects depending on the API version.
        """
        if _version == 1:
            return 'api/v1/project/'
        elif _version == 2:
            return 'api/v2/project/'
        raise Exception( 'Sorry, version %d is not supported by the library yet!' % _version )


class Response(object):

    task = None
    params = {}
    
    def __init__(self, task, dic = None):
        self.task = task
        if dict is not None:
            self.from_dict( dic )

    def dict(self):
        return self.params.copy()

    def from_dict(self, dic):
        self.params = dic

    def to_json(self):
        return json.dumps( self.dict() )

    def from_json(self, JSON):
        self.from_dict( json.loads( JSON ) )

    def __str__(self):
        return self.to_json()
    
    def _getDecisionUrl(self, approve):
        """
        Gets the url for taking a decision on this response.
        """
        suffix = 'approve/' if approve else 'reject/'
        return self.task._getResponsesUrl() + str( self.params['workerId'] ) + '/' + suffix
    
    def _takeDecision(self, approve, reason):
        """
        Takes an approval/rejection decision on this response.
        It return True if the decision was accepted successfully.
        """
        url = self._getDecisionUrl( approve )
        postJson = json.dumps({'reason': reason})
        headers, content = _make_request( url, 'POST', postJson )
        parsedContent = json.loads( content )
        # if the decision fails, throw an exception
        if not parsedContent['success']:
            raise Exception( parsedContent.get( 'error', "Failed: server didn't provide any failure info." ) )
        return True
    
    def approve(self, reason = None):
        """
        Approve this response.
        """
        return self._takeDecision( True, reason )
    
    def reject(self, reason = None):
        """
        Reject this response.
        """
        return self._takeDecision( False, reason )
