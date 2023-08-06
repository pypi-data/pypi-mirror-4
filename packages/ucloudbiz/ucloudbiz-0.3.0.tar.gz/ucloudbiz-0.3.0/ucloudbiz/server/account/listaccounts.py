from ucloudbiz.server.lib.api import UcloudAPI

class listAccounts(UcloudAPI):

    params = {'accounttype'       : [False,None],
              'domainid'       : [False,None],
              'id'             : [False,None],
              'iscleanuprequired'     : [False,None],
              'isrecursive'     : [False,None],
              'keyword'     : [False,None],
              'name'     : [False,None],
              'page'     : [False,None],
              'pagesize'     : [False,None],
              'state'     : [False,None],
              'listall'     : [False,None],
              }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)


