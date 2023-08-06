from ucloudbiz.server.lib.api import UcloudAPI

class listPortForwardingRules(UcloudAPI):

    params = {'account'  : [False,None],
              'domainid' : [False,None],
              'id'       : [False,None],
              'ipaddressid'            : [False,None],
              'keyward'                : [False,None],
              'page'      	       : [False,None],
              'pagesize'               : [False,None],
              'isrecursive'            : [False,None],
              'listall'  	       : [False,None],
              }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

