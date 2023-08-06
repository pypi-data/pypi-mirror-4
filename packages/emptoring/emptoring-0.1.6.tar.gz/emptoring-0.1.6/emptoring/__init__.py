"""
Generic classes for client end of http services




Originally Created 2011 Samuel Smith
Based refactor of Patron to use requests instead of httplib2

See LICENSE.txt for Licensing details
Copyright (c) <2013> <Samuel M. Smith>

"""
import sys
import os
from os import path
import imp
import simplejson as json
import re
import urllib
import lxml.etree
#from xml.parsers.expat import ExpatError
import cStringIO

if sys.version_info[1] < 7: #python 2.6 or earlier
    from ordereddict import OrderedDict as ODict
else:
    from collections import OrderedDict as  ODict

import ssl

import requests 
import pystache

from .lodicting import LODict
from .redirecting import Redirector

_debug = False


class EmptorError(Exception):
    """ Base class for Emptor module exceptions 
        generic exception 
    """
    def __init__(self, msg=''):
        """Create exception instance with attributes
           msg is description
           args is tuple of (msg,)
        """
        self.msg = msg
        self.args = (self.msg,)
    
    def __str__(self):
        """Return string version of exception"""
        return ("%s." % (self.msg))

class KeyEmptorError(EmptorError):
    """Exception resulting from problem with key list
    """
    def __init__(self, msg='', key=None):
        """ Create exception instance with attributes
            msg is description
            key is problem key
            args is tuple of (msg,key)
        """
        super(KeyEmptorError, self).__init__(msg=msg)
        #.msg in superclass
        self.key = key
        self.args = (self.msg, self.key)
        
    def __str__(self):
        """Return string version of exception"""
        return ("%s. key='%s'" % (self.msg,  self.key))

class ReapedEmptorError(EmptorError):
    """Exception resulting from reaped version of response
    """
    def __init__(self, msg='', reaped=None):
        """ Create exception instance with attributes
            msg is description
            reaped is reaped python object
            args is tuple of (msg,reaped)
        """
        super(ReapedEmptorError, self).__init__(msg=msg)
        #.msg in superclass
        self.reaped = reaped
        self.args = (self.msg, self.reaped)
        

class ResponseEmptorError(EmptorError):
    """Exception resulting from problem with http response
    """
    def __init__(self, msg='', response=None,  trace=None):
        """ Create exception instance with attributes
            msg is description
            response is http response object
            args is tuple of (msg,response,)
        """
        super(ResponseEmptorError, self).__init__(msg=msg)
        #.msg assigned in superclass
        self.response = response
        self.trace = trace
        self.args = (self.msg, self.response, self.trace)


class StatusEmptorError(ResponseEmptorError):
    """Exception resulting from failed http response status"""
    
    def __init__(self, msg='', response=None, trace=None, status=None):
        """ Create exception instance with attributes
            msg, response, and trace assigned in superclass
            status parameter is http response status code
            args is tuple of (msg, trace, response, status)
        """
        super(StatusEmptorError, self).__init__(msg=msg,
                                                response=response,
                                                trace=trace)
        #.msg .response in superclass
        self.status = status
        self.args = (self.msg, self.response, self.trace, self.status)
    

class ContentEmptorError(ResponseEmptorError):
    """ Exception resulting from problem with http content
    """
    def __init__(self, msg='', response=None, trace=None, content=None):
        """Create exception instance with attributes
           msg, response, trace assigned in superclass
           args is tuple of (msg,content)
        """
        super(ContentEmptorError, self).__init__(msg=msg,
                                                 response=response,
                                                 trace=trace, )
        self.content = content
        self.args = (self.msg, self.response, self.trace, self.content)
    
        
class XmlEmptorError(ContentEmptorError):
    """Exception resulting from missing or malformed xml content"""
    
    def __init__(self, msg='', response=None, trace=None, content=None, dom=None):
        """Create exception instance with attributes
           msg, response,trace, content assigned in superclass
           
           dom parameter is full parsed xml etree if parses or None
           args is tuple of (msg, response, trace,content, dom)
        """
        super(XmlEmptorError, self).__init__(msg=msg,
                                             response=response,
                                             trace=trace,
                                             content=content,)
        #.msg .response .response.content in superclass
        self.dom = dom
        self.args = (self.msg, self.response, self.content, self.dom)

class JsonEmptorError(ContentEmptorError):
    """Exception resulting from missing or malformed json content"""
    
    def __init__(self, msg='', response=None, content=None, jsn=None):
        """Create exception instance with attributes
           msg, response, trace, content assigned in superclass
           jsn parameter is full parsed json if parses or None
           args is tuple of (msg, response, trace, content, jsn)
        """
        super(JsonEmptorError, self).__init__(msg=msg,
                                              response=response,
                                              trace=trace, 
                                              content=content)
        self.jsn = jsn
        self.args = (self.msg, self.response, self.trace, self.content, self.jsn)
        
    def __str__(self):
        """Return string version of exception"""
        return ("%s.\n content=\n%s json=\n%s" % (self.msg, self.content, repr(self.jsn)))
    

# dict mapping shorthand code for content type and file extension to mime content type
# Did not use python mimetypes module because too many choices for text/plain
# Since data is to be processed by application use application/xml instead of text/xml
CODE_2_MIME_MAP =  {
                        'text' : 'text/plain',
                        'html' : 'text/html',
                        'form' : 'application/x-www-form-urlencoded',
                        'json' : 'application/json',
                        'js'   : 'text/javascript',
                        'xml'  : 'application/xml',
                        'xmlt' : 'text/xml',
                    }

MIME_2_CODE_MAP =  {} #create reverse mapping for reaping from content-type
for key, val in CODE_2_MIME_MAP.items():
    MIME_2_CODE_MAP[val] = key

#Needed to strip unwanted field names derived from xsi attributes in xml
XsiAttributeRe = re.compile(r"^\s*\{[^}]*\}(?P<name>([a-zA-Z_]+[a-zA-Z0-9_]*))\s*$")


class Emptor(object):
    """ Generic Base Class for HTTP REST Service API Client
        
        Class attributes:
            Scheme = optional default http request scheme 'http'
            Port = optional default http request port
            Prefix = default url prefix string
            Hrm = default http request method string ('GET', 'PUT', 'POST', etc)
            Hct = default http request content type string ('xml', 'json','html', 'text')
            Hscs = list of default valid response http status integer codes 
            Hats = list of response default http accept type strings ('xml', 'json','html', 'text')
            
            Preloads = default request data, dict or list of key, value duples
            Headers = default request headers, dict or list of key, value duples
            Creds = optional default dict with keys name password and domain used for authentication
            Xmlns = optional list of default xml namespace urls that is used when reaping xml content
            Mdp = default mold directory path
            Pkcp = client private key and cert path
            Cacp =  certificate authority or host server certs path
            Debug = generate trace if True
            Red = allow redirects if True
            
        
        Instance attributes:
            scheme = url request scheme such as https:// or http://.
            domain = url request domain hostname such as example.com
            port = url request port such as 80
            prefix = url path prefix format string (str.format())
            suffix = url path suffix format string (str.format())
            hrm = http request method string ('GET', 'PUT', 'POST', etc)
            hct = request http content type string. determines mime and file type
                  ('form', xml', 'json', 'html', 'text', etc)
            hscs = list of valid response http status code integers
            hats = list of response http accept type strings. determines mime type
                    ('form', xml', 'json', 'html', 'text', etc)   
            
            preloads = dict or list of key value duples to preload request data dict
            qkeys =  key list to generate request url query arguments
            pkeys =  key list to generate request url path arguments optional
            bkeys =  key list to generate request body data arguments
            headers = dict of http headers, each item (headername, headercontent)
            
            creds = authentication credentials dict optional
            cookies = cookies dict optional
            xmlns = list of xml namespace urls to strip
            debug = generate trace if True
            
            response = requests response object returned from last request
            content = content returned from last request
            trace = http trace of latest request-response
            reaped = reaped content as determined by reaper response content-type
            red = allow redirects if true
            
        
        prefix and suffix detail
            The built in string method format is called on the prefix
                string attribute to generate the request url prefix.
            The built in string method format is also called on the suffix
                string attribute to generate the request url suffix.             
            The full url is
                scheme://domain:portprefixsuffix
            
            The argument to the prefix.format() and suffix.format() call is as follows:
                (**data)  where data is dict composed of the parameters to self.request()
            
            For example given:
                prefix =  '/{service}/' and
                suffix =  'blue/{id}' with
                data = {'service' : 'paint', 'id' : 1542}
            The resulting formatted prefix,  that is, 
                prefix.format(**data) would be: '/paint/'
            The resulting formatted suffix,  that is, 
                suffix.format(**data) would be: 'blue/1542            
            The resulting  path = prefix + suffix, would be:,
                '/paint/color/blue/1542'        
        
        
    """
    #Class attributes read only reference
    
    # Http response status map
    StatusCodeNames =   {
                            200 : "ok" ,
                            201 : "created",
                            202 : "accepted",
                            203 : "non-authoritative information",
                            204 : "no content",
                            205 : "rest content",
                            206 : "partial content",
                            301 : "moved permanently",
                            302 : "found",
                            400 : "bad request",
                            401 : "unauthorized",
                            403 : "forbidden",
                            404 : "not found",
                            406 : "not acceptable",
                            409 : "conflict",
                            412 : "precondition failed",
                            500 : "internal server error",
                            503 : "service unavailable",
                        }
    
    # class relative copies of maps for convenience
    Code2MimeMap = CODE_2_MIME_MAP
    Mime2CodeMap = MIME_2_CODE_MAP
    
    
    #Need this so when run as pipe process the cache directory is in a place 
    
    #Class attributes are default values that should be overridden by subclasses
    Scheme = 'http' # url request scheme
    Domain =  'localhost' # url request host domain  url netloc is domain:port
    Port = '' # url request port
    Prefix = '/' # url path prefix
    Preloads =  ODict() #default data dict preload
    Headers = LODict() # default headers lower cased dict
    Hrm = 'GET' # default request method
    Hct = 'text' # default content type
    Hscs = [200, 201, 202, 203, 204, 205] #status codes
    Hats = []  # accept types empty use Hct
    Creds = {}
    Cookies = {}
    Xmlns = []
    Mdp =  '' #mold directory path
    Pkcp = '' # client private key and cert path
    Cacp = False # certificate authority or server certs path. Don't verify if False
    Debug = False # create trace on requests
    Red = True
    
    def __init__(self, scheme='', domain='', port='', prefix='', suffix='',
            headers=None, hrm='', hct='', hscs=None, hats=None,
            creds=None, cookies=None, xmlns=None, mold='', mdp='',
            preloads=None, qkeys=None, pkeys=None, bkeys=None,
            pkcp='', cacp=None,  red=None, debug=None,  ):
        """ Initialize service instance 
            Parameters:
            
            Optional Default (Use keyword default if not provided)
              suffix = service specific url format string (python2.6 str.format())
              mold = service specific mold file
              qkeys = service specific query arg key list
              pkeys = service specific path arg key list
              bkeys = service specific body arg key list
              
            Optional Override (These override associated class values if not empty)
              scheme = server URL scheme
              domain = server URL domain
              port = server URL port
              prefix = server prefix URL string, including scheme, host, port at least
              preloads = default data dict
              headers = service specific headers
              hrm = http request method string ('GET' 'PUT' 'POST' etc)
              hct = http content type string ('xml' or 'json')
              hats = list of http accept type strings ('xml' or 'json')
              hscs = list of http status codes for statusfy
              creds = authentication credentials dictionary
              cookies = dict of cookies
              xmlns = list of xml namespace urls to strip
              mdp = mold directory path
              pkcp = private key and cert path
              cacp = cert auth path or False if ignore
              debug = create trace
              red = allow redirects
              
        """
        # optional parameters, 
        self.scheme = scheme or self.Scheme
        self.domain = domain or self.Domain
        self.port =  port or self.Port
        self.prefix = prefix or self.Prefix
        self.suffix = suffix #no class default
        
        self.preloads = ODict(self.Preloads) #copy call default .Preload
        self.preloads.update(preloads or []) #update with preload if not empty
        
        self.headers = LODict(self.Headers) #lowercase keys with LODict
        self.headers.update(headers or [])
        
        # optional, use parameter if not empty else use class attribute
        self.hrm = (hrm or self.Hrm).upper() #ensure uppercase
        self.hct = (hct or self.Hct).lower() #ensure lowercase
        self.hscs = hscs or list(self.Hscs) #make copy of list Hscs
        # use [.hct] for .hats if .hat is not provided otherwise
        self.hats = [hat.lower() for hat in (hats or list(self.Hats) or [self.hct])]
        
        if creds is None:
            creds = dict(self.Creds)
        self.creds = {}
        for key, value in creds.items(): #make local copy
            self.creds[key.lower()] = value
        
        if cookies is None:
            cookies = dict(self.Cookies)
        self.cookies = {}
        self.cookies.update(cookies)
        
        if xmlns is None:
            xmlns = []
        self.xmlns = list(xmlns) or list(self.Xmlns)
        self.red = self.Red if red is None else True if red else False
        self.debug = self.Debug if debug is None else True if debug else False
        
        #other
        self.response = None
        self.trace = None # debug string
        self.reaped = None
        
        # derived
        #set content-type header based based on .hct
        mime = self.Code2MimeMap.get(self.hct,None)
        if mime:
            self.headers['content-type'] = mime
        
        #set accept header based based on .hats
        mimes = [self.Code2MimeMap.get(hat,None) for hat in self.hats if self.Code2MimeMap.get(hat,None)]
        if mimes:
            self.headers['accept'] = ','.join(mimes)        
          
        #default no caching
        if 'cache-control'  not in self.headers:
            self.headers['cache-control']  = 'no-cache, no-store, must-revalidate'
          
        #assign reaper method based on first element in .hats attribute (http accept type)
        try: 
            reaper = "reap%s" % (self.hats[0].capitalize())
            self.reaper = getattr(self, reaper)
        except AttributeError:
            self.reaper = self.reap #use default reaper
        
        self.mold = mold
                
        if qkeys is None:
            qkeys = []        
        self.qkeys = list(qkeys) #make local copy
        
        if pkeys is None:
            pkeys = []        
        self.pkeys = list(pkeys) #make local copy
        
        if bkeys is None:
            bkeys = []        
        self.bkeys = list(bkeys) #make local copy        
        
        self.pkcp = pkcp or self.Pkcp
        self.cacp = self.Cacp if cacp is None else cacp
        
        # optional, use parameter if not empty else use class attribute
        self.mdp = (mdp or self.Mdp)
        
        """ Do some intelligent path manipulation to simplify rosters. 
            The policy is that by default template (mold) files are stored in
            a subdirectory named after the file type extension such as
            one of [xml, json, text, html] 
            that is in turn in a subdirectory named given by self.mdp
            for example templates/xml/create.xml  or templates/text/create.text
            
            The provided mold filename must either be, 
            the base filename without prefixed subdirectories or extension or 
            it it must be a valid path including extension
            If the former then add the prefixes and extension based on the .hct. 
            If the latter verify the .hct matches  the extension 
            The latter case only assumes that a valid file path is provided and does
            not require that the file be in the mdp/xxx subdirectory
        """
        if self.mold:
            self.mold = path.normpath(self.mold) #normalize path 
            root, ext = path.splitext(self.mold)
            head, base = path.split(root)
            if not ext and not head: #bare base so build full name
                self.mold = path.normpath("%s/%s/%s.%s" % 
                        (self.mdp,self.hct,base,self.hct)) #normpath fixes separators                
            
            else: #verify extension
                if ext.lower() != '.' + self.hct: 
                    raise ValueError(("Invalid template file type: "
                                        "extension '%s' not match content type'%s'")
                                                            % (ext, self.hct))        
    
    def __call__(self, *pa, **kwa):
        """Calls request method of instance"""
        return (self.request(*pa, **kwa))

    def verify(self):
        """Check response and content for errors. Raise exeception if found.
        
            Subclasses should override this method with service specific verification
        """
        self.statusfy()
        self.typify()
        
    def statusfy(self):
        """Check for valid http status on response, Raise exception if not. 
          
            Subclasses should override this method 
        """
        if self.response.status_code not in self.hscs: #not acceptable status code 
            msg = ("Http response status = '%s' '%s'"
            % (self.response.status_code, self.StatusCodeNames.get(
                self.response.status_code, 'unknown')))
            raise StatusEmptorError(msg=msg,
                                    response=self.response,
                                    trace=self.trace,
                                    status=self.response.status_code)

    def typify(self): 
        """ Check content type to see if it is included in .hats
            Raise exception if not 
        
            Subclasses should override this method.
        """
        contentTypes = self.response.headers.get('content-type','')
        for hat in self.hats:
            if self.Code2MimeMap.get(hat,'') in contentTypes:
                return
            
        raise ContentEmptorError(msg = ("Invalid http response content-type. "
                                          "from service request " 
                                        "Accepted '%s' but got '%s'.")
                    % (self.headers['accept'], self.response.headers.get('content-type','')),
                        response=self.response, content=self.response.content)     

    def ratify(self):
        """Check reaped  dict for failure indicator. Raise exception if failure
            Subclasses should override this method with service specific checks.
        """
        pass   
                  
    def reap(self):
        """Default reap method is to return content unaltered as value"""
        self.reaped = self.response.content
        return self.reaped
    
    def reapJs(self):
        """ Reap javascript same as json"""
        return self.reapJson()
        
    def reapJson(self):
        """ Convert json content if any to python object
        """
        self.reaped = ''
        if self.response.content:
            try:
                self.reaped = json.loads(self.response.content)
            except ValueError:
                raise ContentEmptorError(msg = "Invalid 'content' not json", 
                                            content = self.response.content)
        return self.reaped
    
    def reapXml(self):
        """ Convert xml to elementree then traverse tree creating hierarchical 
            python dict of values, lists, and/or dicts.
            Essentially the python representation of json equivalent of the xml.
            Xml attribute names will have '@' prepended
        """
        self.reaped = ''
        if self.response.content:
            try:    
                root = lxml.etree.fromstring(self.response.content) #get root element
            except (SyntaxError, ) as ex:
                raise ContentEmptorError(msg = "Invalid 'content' not xml", 
                                            content = self.response.content)
            
            #add brackets to xmlns url strings
            xmlns = ['{%s}' % ns for ns in self.xmlns]
            #walk tree here generating hierarchical dict of values, lists, dicts
            self.reaped = self.walk(root, xmlns)
        
        return self.reaped
    
    @staticmethod
    def walk(e, xmlns=[]):
        """Recursively build hierarchical dict from elementtree element e"""
        d = {} #assume dict representation of e but may be string if tip
            
        #add xml attributes of e which are provided in items() list 
        for k,v in e.items(): 
            sre = XsiAttributeRe.search(k) #strip off any xsi attribute urls in name
            if sre:
                k = sre.group('name')
            d['@%s' % k] = v #prepend '@' to key and add to d
            #d[k] = v #add xml attribute to d
          
        nodes = list(e)#list operation extracts e's nodes into list
        if not nodes: # empty list means no nodes so e is tip element
            if d: #d has xml attributes so insert e's text as "value"
                d['value'] = e.text #add element's text as value
            else: # d no xml attributes so return plain string
                d = e.text
        else: #not tip element so walk down 
            for node in nodes: #iterate over nodes 
                walked = Emptor.walk(node, xmlns) #do once here since 'try except' may walk twice
                tag = node.tag
                for ns in xmlns:
                    if tag.startswith(ns): #strip off namespace prefix
                        tag = tag.replace(ns, '', 1)
                if tag not in d: #first time this tag seen for this element
                    d[tag] = walked #walked node as value of this key
                else: #not first time so attach as list of subelements with tag
                    try: #try to append to list
                        d[tag].append(walked) #
                    except AttributeError: # not yet a list, so make it one
                        d[tag] = [d[tag],walked]
        
        return d  # all done
       
    def begetDataBody(self, *pa, **kwa):
        """ Returns duple (data,body) for request from arguments
            positional arguments may be either strings, sequences of key,value
            duples, or dictionaries.
            
            Body is string concated from all string positional arguments.
            Non string positional arguments and keyword arguments are ignored.
            
            Data is an ordereddict where the items are extracted from the
            any sequenced duples and/or dicts in the positonal arguments and from
            the keyword arguments.
            String positional arguments are ignored.
        """
        body = ''
        data = ODict(self.preloads) #load defaults

        for a in pa: #extract key/value pairs from positional parameters
            if isinstance(a, basestring): # string
                body = '%s%s' %  (body,  a) #concat
            else: # dict or sequence of duples
                data.update(a)
    
        data.update(kwa) #so insert keyword arguments
        
        if isinstance(body, unicode):
            body = body.encode('utf-8')
            if 'utf-8' not in self.headers['content-type']:
                self.headers['content-type'] += '; charset=utf-8'        
        
        return (data, body)
    
    
    def begetPathArgs(self, data):
        """ Create pargs for url path generation from pkeys if given
            Do urlencoding
            return pargs dict
        """
        pargs = ODict() 
        # assign values from kwa for pkeys
        for key in self.pkeys:
            try:
                pargs[key] = data[key]
            except KeyError as ex:
                raise KeyEmptorError(msg = "Missing data for path key.",key=key)                
    
        for key, val in pargs.items():
            pargs[key] = urllib.quote(val, '/:;#')
        
        return pargs


    def begetQueryArgs(self, data):
        """ Build query args from data and self.qkeys"""
        qargs = ODict()
        for key in self.qkeys:
            qargs[key] = data.get(key, '')
        
        return qargs
    
    
    def buildUrl(self, data):
        """ Build and return url for request from attributes and data dict
            Url includes the scheme, netloc path, port, and separators.
            Everything in the url except the query string.
        """
        pargs = self.begetPathArgs(data) or data #use pargs if not empty else use data
        #build request url
        url = "%s://%s%s%s%s" % (self.scheme,
                               self.domain.format(**pargs),
                               ((':%s' % self.port) if self.port else '' ), 
                               self.prefix.format(**pargs),
                               self.suffix.format(**pargs), )        
        url= urllib.quote(url, '/:;#')
        
        return url

    def buildBody(self, data, body=''):
        """ Build body for request from attributes and data
            data is a dict.
            body is optional body string
            
            If body is not empty then return body
            Otherwise
               build the body appropriately from data
        """
        if not body:
            bargs = ODict()
            for key in self.bkeys: #filter data by bkeys
                try:
                    bargs[key] = data[key]
                except KeyError as ex:
                    raise KeyEmptorError(msg = "Missing data for body key.",key=key) 
        
            data = bargs or data #If no bkeys then bargs empty so use all of data
            if data:
                if self.hct == 'form' and self.hrm != 'GET': #send as form encoded
                    body = urllib.urlencode(data) #encode as key=value&... string       
            
                elif self.hct == 'json' and self.hrm != 'GET': #json
                    body = json.dumps(data, indent=2, sort_keys=True)
                
                elif self.mold:  #build from template
                    body = self.render(data) #render template
            
        
        if isinstance(body, unicode):
            body = body.encode('utf-8')
            if 'utf-8' not in self.headers['content-type']:
                self.headers['content-type'] += '; charset=utf-8'
        
        return body
    
    def render(self, data):
        """ Render body content from self.mold and data dictionary
            Currently uses mustache pystache
        """
        renderer = pystache.Renderer()
        body = renderer.render_path(self.mold, data)
            
        return body    
                
    
    
    def request(self, *pa, **kwa):
        """ Generate and send request associated with service instance 
            Positional parameters may be either  strings or dicts or sequences
            of (key, value) duples. If the first positional parameter is a string
            then all non string parameters are ignored and all string parameters
            are concatenated to form a data string.
            Otherwise key value pairs, from either the sequences or dicts
            are extracted and then inserted as items in data dict
            
            Use attributes and parameters and template to generate url
            (path and query args), request method, 
            content type and content.
            
            Specifically the optional self.mold file is used as
            a template to generate the content. Because all three path, query args
            and content are template based we combine all parameters to this call
            into one context dictionary and then let the templates pull out the
            values they need, 
            Return successful response content payload otherwise raise exception
        
            
        """
        data, body = self.begetDataBody( *pa, **kwa)
        url =  self.buildUrl(data)
        qargs =  self.begetQueryArgs(data)
        body =  self.buildBody(data, body)
        
        auth = tuple([value for key, value in self.creds.items()
                      if key in ['user', 'pass']]) or None
        
        if self.debug:
            import httplib
            httplib.HTTPConnection.debuglevel = 5
            #requests.packages.urllib3.add_stderr_logger()
            # see https://github.com/kennethreitz/requests/issues/988#issuecomment-11049812
            """ requests.request(method, url, **kwargs)
                Constructs and sends a Request. Returns Response object.
                
                Parameters:
                method  method for the new Request object.
                url  URL for the new Request object.
                qargs  (optional) Dictionary or bytes to be sent in the query string for the Request.
                data  (optional) Dictionary or bytes to send in the body of the Request.
                headers  (optional) Dictionary of HTTP Headers to send with the Request.
                cookies  (optional) Dict or CookieJar object to send with the Request.
                files  (optional) Dictionary of name: file-like-objects (or {name: (filename, fileobj)}) for multipart encoding upload.
                auth  (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
                timeout  (optional) Float describing the timeout of the request.
                allow_redirects  (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
                proxies  (optional) Dictionary mapping protocol to the URL of the proxy.
                verify  (optional) if True, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
                stream  (optional) if False, the response content will be immediately downloaded.
                cert  (optional) if String, path to ssl client cert file (.pem). If Tuple, (cert, key) pair.
            """        
        try:
            
            with Redirector() as redstd: #redirect stdout, stderr to string
                #print "body:\n%s" %  body
                response = requests.request(url=url,
                                            method=self.hrm,
                                            params = qargs, 
                                            data=body, 
                                            headers=self.headers,
                                            cookies=self.cookies,
                                            verify=self.cacp,
                                            cert=self.pkcp,
                                            auth=auth,
                                            allow_redirects=self.red) 
                
                self.response = response
                if self.debug:
                    redstd.seek(0) #go to head of file
                    trace = ''
                    for line in redstd: #strip out raw string escapes and reformat
                        if line.startswith('send: '):
                            trace = "%sRequest: \n\n%s" % (trace, 
                                line.lstrip("send: '").rstrip("'\n").decode('string_escape'))
                        elif line.startswith('reply: '):
                            trace = "%s\n\nResponse: \n\n%s" % (trace, 
                                line.lstrip("reply: '").rstrip("'\n").decode('string_escape'))
                        elif line.startswith('header: '):
                            trace = "%s%s" % (trace, line.lstrip("header: "))
                    self.trace = "%s\n%s" %  (trace, response.content)
                    
                    
        except Exception as e:
            raise    
        
        #check response for error, raises exception if error found
        self.verify()
        
        self.reaper() #reap hierarchical python dict from content.
        
        #check reaped content for application error. raises exception on error
        self.ratify() 
        
        return self.reaped     

class Emptory(object):
    """ Emptory class is a factory to generate a container object instance
        whose attributes are references to a group of related Emptors. 
        One Emptory instance provides client interfaces 
           to a group of related services
        Attribute Names are derived from roster list
          'name' item in roster list entry becomes attribute reference 
              of associated emptor instance
        
        Usage:
            roster = [{'name' : 'test', 'suffix' : 'me']
            emptory = Emptory(roster)
            reaped = emptory.test()
         
        If given, the roster entry's help items are combined and prepended to the
        emptory instance's _helps attribute (not .__doc__)
        
        The emptory's _emptors attribute is a dict of the patrons with names as keys.
    """
    def __init__(self, roster, emptorist=Emptor, **kwa):
        """ Create container group of emptor instances defined by roster
            Parameters:
                roster = list of dicts with some required and some optional keys
                default values will be used for optional keys when missing
                patroner = reference to Emptor subclass to be used to generate 
                        emptor instances
                
                The rest of the init args are passed to _rosterate to process
                   for default values etc.
        """
        helps = []
        self._emptors = ODict() #ordered dict of patrons in patronage
        for entry in roster:
            name = entry['name'] #required
            helps.append("%s: %s" % (name, entry.get('help','')))
            initargs = self._rosterate(entry, **kwa) #process init args and roster keys
            #create emptor instance and assign to attribute name
            emptor = emptorist(**initargs)
            self._emptorize(name, emptor, helps[-1]) 
            self._emptors[name] = emptor # for introspection
        
        self._helps = '\n'.join(helps) #list of helps

    def _rosterate(self, entry, scheme='', port='', domain='', prefix='',
                   suffix='', preloads=None, headers=None, 
                   hrm='', hct='',hscs=None, hats=None,
                   creds=None, xmlns=None, mdp='', pkcp='', cacp=False,
                   debug=False,  red=True):
        """ Generate emptor init args for the given entry and init parameters. 
            Parameters
                scheme = Server URL scheme
                port = Server URL port
                domain = Server URL domain 
                prefix = Server URL path prefix string
                suffix = Server URL path suffix string
                preloads = dict of default preloads for data dict
                headers = dict of default headers
                hrm = http request method string
                hct = request http content-type key
                hscs = response http status code list
                hats = response http accept type key list
                creds = http authentication credentials dict
                xmlns = list of xml namespace strings to strip from response
                mdp = mold directory path
                pkcp = private key cert path
                cacp = certificate authority certs path
                debug = create and save httplib trace
                red = allow redirects
                
            Special processing of parameters to this function
                The final instance attributes value will be.
                    The roster value if associated item is provided and not
                        empty or None
                    Else the associated parameter to this function if not
                        empty or None
                    Else the associated class attribute default when the emptor
                        is finally inited
            
            
            The possible roster keys are as follows:
                'name' required name for emptor
                'help' optional = string describes service method
                'scheme' optional
                'domain' optional
                'port' optional
                'prefix' optional
                'suffix' optional
                'preloads' optional
                'headers' optional
                'hrm' optional
                'hct' optional
                'hscs' optional
                'hats' optional
                'creds' optional
                'xmlns' optional
                'mdp' optional
                'mold' optional
                'qkeys' optional
                'pkeys' optional
                'bkeys' optional
                'pkcp' optional
                'cacp' optional
                'debug' optional
                'red' optional
                
                
                    
        """
        ia={}
        #default for all services with service specific override
        ia['scheme'] = entry.get('scheme', '') or scheme
        ia['domain'] = entry.get('domain', '') or domain
        ia['port'] = entry.get('port', '') or  port
        ia['prefix'] = entry.get('prefix', '') or prefix
        ia['preloads'] = entry.get('preloads', None) or preloads
        ia['headers'] = entry.get('headers', None) or headers
        ia['hrm'] = entry.get('hrm', '') or hrm
        ia['hct'] = entry.get('hct', '') or hct
        ia['hscs'] = entry.get('hscs', None) or hscs
        ia['hats'] = entry.get('hats', None) or hats
        ia['creds'] = entry.get('creds', None) or creds
        ia['xmlns'] = entry.get('xmlns', None) or xmlns
        ia['mdp'] = entry.get('mdp', '') or mdp
        ia['pkcp'] = entry.get('pkcp', '') or pkcp
        ia['cacp'] = entry.get('cacp', False) or cacp
        ia['debug'] = entry.get('debug', False) or debug
        ia['red'] = entry.get('red', False) or red
        #service specific
        ia['suffix'] = entry.get('suffix', '')
        ia['mold'] = entry.get('mold', '')  
        ia['qkeys'] = entry.get('qkeys', None)
        ia['pkeys'] = entry.get('pkeys', None)
        ia['bkeys'] = entry.get('bkeys', None)        

        return ia
        
    def _emptorize(self, name, emptor, help = ""):
        """ Create  and assign emptor attribute 'name' so call of attribute 
            will call emptor.request
            Set doc string of emptor to include help for introspection
        """
        if help:
            emptor.__doc__ = "%s\n%s" % (help, emptor.__doc__)
        
        setattr(self, name, emptor)
