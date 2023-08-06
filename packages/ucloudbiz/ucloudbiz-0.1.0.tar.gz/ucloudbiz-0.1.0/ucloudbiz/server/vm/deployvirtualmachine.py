from ucloudbiz.server.lib.api import UcloudAPI

class deployVirtualMachine(UcloudAPI):

    params = {'serviceofferingid' : [True,None],
              'templateid'        : [True,None],
              'diskofferingid'    : [True,None],
              'zoneid'            : [True,None],
              'name'              : [False,None],
              'networkids'        : [False,None],
              'userdata'          : [False,None],
              }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

