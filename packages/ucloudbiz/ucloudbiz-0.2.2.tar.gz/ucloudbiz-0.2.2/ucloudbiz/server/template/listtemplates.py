from ucloudbiz.server.lib.api import UcloudAPI

class listTemplates(UcloudAPI):

    params = {	'templatefilter' : [True,None],
              	'account'       : [False,None],
      		'domain'    	: [False,None],
      		'hypervisor'    : [True,None],
      		'id'            : [False,None],
      		'keyword'       : [False,None],
      		'name'          : [False,None],
		'name' 		: [False,None],
		'page' 		: [False,None],
		'pagesize'	: [False,None],
		'zoneid'  	: [False,None],
		'isrecursive'	:[False,None],
		'listall'	:[False,None]
      }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

