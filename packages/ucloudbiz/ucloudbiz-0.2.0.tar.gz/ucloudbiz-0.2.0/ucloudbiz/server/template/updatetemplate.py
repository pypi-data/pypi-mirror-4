from ucloudbiz.server.lib.api import UcloudAPI

class updateTemplate(UcloudAPI):

    params = {	'id' 			: [True,None],
              	'bootable'      : [True,None],
				'displaytext'   : [True,None],
				'format'    	: [True,None],
				'name'          : [False,None],
				'ostypeid'      : [False,None],
				'passwordenabled' 	: [False,None],
				'sortkey'			:[False,None]
			  }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

