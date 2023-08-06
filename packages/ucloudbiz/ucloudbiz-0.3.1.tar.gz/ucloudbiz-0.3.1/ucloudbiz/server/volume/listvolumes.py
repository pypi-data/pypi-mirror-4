from ucloudbiz.server.lib.api import UcloudAPI

class listVolumes(UcloudAPI):

    params = { 'account'    : [False,None],
      			'domainid'  : [False,None],
      			'hostid'   	: [False,None],
      			'isrecursive'           : [False,None],
      		'keyword'       : [False,None],
      		'name'          : [False,None],
		'page' 		: [False,None],
		'pagesize'	: [False,None],
		'podid'  	: [False,None],
		'type'	:[False,None],
		'virtualmachineid'	:[False,None],
		'zoneid'	:[False,None],
		'listall'	:[False,None]
      }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

