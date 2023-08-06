from ucloud.lib.api import UcloudAPI

class queryAsyncJobResult(UcloudAPI):

    params = {'jobid' : [True,None],
              }
    
    def __init__(self, url=None, apikey=None, secret=None):
        UcloudAPI.__init__(self, url, apikey, secret)

    def getResult(self, result):
        # @param result : result dictionary
        # key : queryasyncjobresultresponse
        rvalue = result['queryasyncjobresultresponse']
        return (int(rvalue['jobstatus']), rvalue)

