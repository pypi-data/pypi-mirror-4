from ucloudbiz.server.lib.api import UcloudAPI

class createFirewallRule(UcloudAPI):

    params = {'ipaddressid'  : [True,None],
              'protocol' : [True,None],
              'cidrlist'       : [False,None],
              'startport'            : [False,None],
              'endport'                : [False,None],
              'icmpcode'      	       : [False,None],
              'icmptype'               : [False,None],
              'type'            : [False,None],
              }
    
    def __init__(self):
        UcloudAPI.__init__(self)

    

