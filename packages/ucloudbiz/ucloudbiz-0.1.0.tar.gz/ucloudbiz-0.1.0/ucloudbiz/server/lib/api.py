import urllib
import urllib2
from hashlib import sha1
import hmac
import binascii

class UcloudAPI:
    URL=None
    APIKEY=None
    SECRET=None
    RESPONSE='json'
    # format 
    #  key : [required(True/False), value]
    params = {}
    
    def __init__(self, url=None, apikey=None, secret=None):
        self.URL = url
        self.APIKEY = apikey
        self.SECRET = secret
        
    def helpParams(self):
        keys = self.params.keys()
        print "Parameter List"
        for key in keys:
            [tf, value] = self.params[key]
            if tf == True:
                print "%s\trequired" % key
            else:
                print "%s\toptional" % key

    def showParams(self):
        keys = self.params.keys()
        print "Parameter List"
        for key in keys:
            [tf, value] = self.params[key]
            if tf == True:
                print "%s\t= %s\t(required)" % (key, value)
            else:
                print "%s\t = %s\t(optional)" % (key, value)
                                                                                
                
    def checkParams(self):
        keys = self.params.keys()
        for key in keys:
            [tf, value] = self.params[key]
            if tf == True:
                if value == None:
                    print "Error: param(%s=%s) must exist" % (key, value)

    def updateParams(self, dic):
        """
        update self.params based on dic
        """
        keys = self.params.keys()
        for key in keys:
            if dic.has_key(key) == True:
                (tf, value) = self.params[key]
                self.params[key] = (tf, dic[key])
            #clean up, garbage if possible
            else:
                (tf, value) = self.params[key]
                self.params[key] = (tf, None)
        #self.showParams()
        
        
    def setURL(self, url):
        self.URL = url

    def setAPIKEY(self, apikey):
        self.APIKEY = apikey

    def setSECRET(self, secret):
        self.SECRET = secret


    def createAPI(self):
    	#
	real_params = {'command':self.__class__.__name__}
	real_params['apikey'] = self.APIKEY
	real_params['signature'] = self.createSignature()
	real_params['response'] = self.RESPONSE
	keys = self.params.keys()
	for key in keys:
	    test = self.params[key]
	    if test[1] == None:
	       continue
	    real_params[key] = test[1]

        url_params = urllib.urlencode(real_params).replace('+','%20')	
	return "%s%s" % (self.URL, url_params)
	 
    def createSignature(self):
        # filter real parameters
        keys = self.params.keys()
        # add command name
        real_params = {'command':(self.__class__.__name__).lower()}
        for key in keys:
	    test = self.params[key]
            if test[1] == None:
                continue
	    low_str = test[1]
	    try:
		toLower = low_str.lower()
	    except:
		#This seems like Number
		toLower = low_str
            real_params[key.lower()] = toLower
            
        # add response type
        real_params['response'] = (self.RESPONSE).lower()
        # add apikey
	low_str = self.APIKEY
        real_params['apikey'] = low_str.lower()
         
        url_params = urllib.urlencode(real_params).replace('+','%20')

	#print url_params
	items = url_params.split("&")
	url_params_new = {}
	for item in items:
	    index = item.find("=")
	    url_params_new[item[:index]]=item[(index+1):]
	url_keys = url_params_new.keys()
        url_keys.sort()
        cmd_str = ""
        for key in url_keys:
            cmd_str = cmd_str + "%s=%s&" % (key, url_params_new[key])

        #TEST
        cmd_str2 = cmd_str[:-1].lower()
        hashed = hmac.new(self.SECRET, cmd_str2, sha1)
        signature = binascii.b2a_base64(hashed.digest())[:-1]
        print "signature:\n%s" % signature
	return signature
         

         
    def execute(self, param=None):
        #Override
        #before execute, call paramCheck()
	if param != None:
	   self.updateParams(param)
	self.checkParams()
        cmd = self.createAPI()
        print "#"*40
	print "Requesting URL:\n%s" % cmd
        print "#"*40
        try:
            f = urllib2.urlopen(cmd)
            result = f.read()
        except:
            yn = raw_input("Call again(y/n)")
            if yn.lower() == "y":
                return self.execute(param)
            else:
                return False
            
	return result
	

    def parseJsonResult(self, result):
    	import json
    	args = json.loads(result)
    	return args

    def parseAsyncResult(self, dic):
    	keys = dic.keys()
	# key may be 1
	if len(keys) != 1:
	   print "Warning:%s" % dic
	key = keys[0]
	job = dic[key]
	id = job['id']
	jobid = job['jobid']
	return jobid
	    
