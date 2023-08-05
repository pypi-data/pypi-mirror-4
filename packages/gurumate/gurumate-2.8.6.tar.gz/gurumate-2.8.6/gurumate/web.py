import urllib2
from gurumate.base import fail
from urllib2 import HTTPError, URLError

def check_url_accessibility(url, timeout=10):       
    '''
    Check whether the URL accessible and returns HTTP 200 OK or not
    if not raises ValidationError
    '''
    if(url=='localhost'):
        url = 'http://127.0.0.1'
    try:
        req = urllib2.urlopen(url, timeout=timeout)
        if (req.getcode()==200):
            return True
    except Exception:
        pass
    fail("URL '%s' is not accessible from this machine" % url)
    
def url_has_contents(url, contents, case_sensitive=False, timeout=10):
    ''' 
    Check whether the HTML page contains the content or not and return boolean
    '''
    try:    
        req = urllib2.urlopen(url, timeout=timeout)
    except Exception, _:
        False
    else:
        rep = req.read()
        if (not case_sensitive and rep.lower().find(contents.lower()) >= 0) or (case_sensitive and rep.find(contents) >= 0):
            return True
        else:
            return False

def get_response_code(url, timeout=10):
    '''
    Visit the URL and return the HTTP response code in 'int'
    '''
    try:    
        req = urllib2.urlopen(url, timeout=timeout)
    except HTTPError, e:
        return e.getcode()
    except Exception, _:
        fail("Couldn't reach the URL '%s'" % url)
    else:
        return req.getcode()

def check_response_code(url, code, timeout=10):
    try:
        resp = get_response_code(url, timeout=timeout)
    except:
        return False

    if  resp != code:
        fail("The URL '%s' is reachable but returns HTTP response code of '%s' while I expected '%s'" % (url, resp, code))
        
def compare_content_type(url, content_type):
    '''
    Compare the content type header of url param with content_type param and returns boolean 
    @param url -> string e.g. http://127.0.0.1/index
    @param content_type -> string e.g. text/html
    '''
    try:    
        response = urllib2.urlopen(url)
    except:
        return False

    return response.headers.type == content_type

def compare_response_code(url, code):
    '''
    Compare the response code of url param with code param and returns boolean 
    @param url -> string e.g. http://127.0.0.1/index
    @param content_type -> int e.g. 404, 500, 400 ..etc
    '''
    try:
        response = urllib2.urlopen(url)
    
    except HTTPError as e:
        return e.code == code
    
    except:
        return False

    return response.code == code
