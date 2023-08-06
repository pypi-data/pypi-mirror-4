from ucloudbiz.server.lib.api import UcloudAPI

class deleteTemplate(UcloudAPI):

    params = {	'id' : [True,None],
              	'zoneid'       : [False,None]
		  }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

