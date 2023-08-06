from ucloudbiz.server.lib.api import UcloudAPI

class listPublicIpAddresses(UcloudAPI):

    params = {'account'       : [True,None],
              'allocatedonly' : [False,None],
              'domainid'       : [False,None],
              'forvirtualnetwork'      : [False,None],
              'id'     : [False,None],
              'ipaddress'     : [False,None],
              'keyword'     : [False,None],
              'page'     : [False,None],
              'pagesize'     : [False,None],
              'vlanid'     : [False,None],
              'associatednetworkid'     : [False,None],
              'isrecursive'     : [False,None],
              'issourcenat'     : [False,None],
              'isstaticat'     : [False,None],
              'listall'     : [False,None],
              'physicalnetworkid'     : [False,None],
              }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)


