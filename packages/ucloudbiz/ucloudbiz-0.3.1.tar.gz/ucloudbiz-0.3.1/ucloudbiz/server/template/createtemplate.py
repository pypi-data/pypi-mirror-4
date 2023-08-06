from ucloudbiz.server.lib.api import UcloudAPI

class createTemplate(UcloudAPI):

    params = {	'displaytext' : [True,None],
              	'name'       : [True,None],
      		'ostypeid'    	: [True,None],
      		'bits'    : [False,None],
      		'details'            : [False,None],
      		'isfeatured'       : [False,None],
      		'ispublic'          : [False,None],
		'passwordenabled' 		: [False,None],
		'requireshvm' 		: [False,None],
		'snapshotid'	: [False,None],
		'templatetag'  	: [False,None],
		'url'	:[False,None],
		'virtualmachineid'	:[False,None],
		'volumeid'	:[False,None]
      }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

