from ucloudbiz.server.lib.api import UcloudAPI

class associateIpAddress(UcloudAPI):

    params = {'zoneid'        : [False,None],
              'usageplantype' : [False,None],
              'account'       : [False,None],
              'domainid'      : [False,None],
              'networkid'     : [False,None],
              }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)


