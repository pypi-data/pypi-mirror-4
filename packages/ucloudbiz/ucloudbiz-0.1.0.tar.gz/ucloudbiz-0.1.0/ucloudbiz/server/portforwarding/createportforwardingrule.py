from ucloudbiz.server.lib.api import UcloudAPI

class createPortForwardingRule(UcloudAPI):

    params = {'ipaddressid'  : [True,None],
              'privateport'  : [True,None],
              'protocol'     : [True,None],
              'publicport'   : [True,None],
              'virtualmachineid'  : [True,None],
              'cidrlist'       : [False,None],
              'openfirewall'            : [False,None],
              'privateendport'                : [False,None],
              'publicendport'      	       : [False,None],
              }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    

