from ucloudbiz.server.lib.api import UcloudAPI

class listAvailableProductTypes(UcloudAPI):

    params = {
				'zoneid':[False,None]
              }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

