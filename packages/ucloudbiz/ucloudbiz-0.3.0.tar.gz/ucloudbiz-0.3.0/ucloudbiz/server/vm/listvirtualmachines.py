from ucloudbiz.server.lib.api import UcloudAPI

class listVirtualMachines(UcloudAPI):

    params = {
        'account' : [False,None],
        'domainid' : [False,None],
        'forvirtualnetwork' : [False, None],
        'groupid' : [False, None],
        'hostid' : [False, None],
        'hypervisor' : [False, None],
        'id' : [False, None],
        'isrecursive' : [False, None],
        'keyword' : [False, None],
        'name' : [False, None],
        'networkid' : [False, None],
        'page' : [False, None],
        'pagesize' : [False, None],
        'podid' : [False, None],
        'state' : [False, None],
        'storageid' : [False, None],
        'zoneid' : [False, None],
        'details' : [False, None],
        'listall' : [False, None],
        }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

