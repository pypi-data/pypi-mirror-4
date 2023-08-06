#!/usr/bin/env python
from ucloudbiz.server.vm.listvirtualmachines import listVirtualMachines

#########################################################################################
# Reference: http://developer.ucloudbiz.olleh.com/doc/cloudstack/VM/listVirtualMachines/
##########################################################################################
#For Logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('ucloudbiz-test')
hdlr = logging.FileHandler('./ucloudbiz-test.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

def run(url, apikey, secret):
	logger.debug("Run API")
	inst = listVirtualMachines(url, apikey, secret)

	param = {'state':'Stopped'}
	result = inst.execute(param)
	dic = inst.parseJsonResult(result)
	response = dic['listvirtualmachinesresponse']
	vms = response['virtualmachine']
	for vm in vms:
		print vm

if __name__ == "__main__":

	from optparse import OptionParser
	usage = "usage: %prog [options] arg"
	parser = OptionParser()

	parser.add_option("-a","--apikey", dest="apikey",help="API Key")
	parser.add_option("-s","--secret", dest="secret",help="Secret Key")
	parser.add_option("-u","--url", dest="url",help="API Server URL")

	(options,args) = parser.parse_args()

	if not options.apikey:
		apikey = raw_input("APIKEY=>")

	else:
		apikey = options.apikey
 	
	if not options.secret:
	  	secret = raw_input("SECRET=>")
 	else:
		secret = options.secret

	if not options.url:
		url = "https://api.ucloudbiz.olleh.com/server/v1/client/api?"

	else:
		url = options.url

	logger.debug("############## Start to Call API #############")
	logger.debug("APIKEY:%s" % apikey)
	logger.debug("SECRET:%s" % secret)
	print "\n\n\n\n"
	print "########### Warning ###########################"
	print "API URL : %s" % url
	print "###############################################"
	print "\n\n"
   	yn = raw_input("URL is corrent(y/n)")
	if yn.lower() != "y":
		print "Exiting...."
		sys.exit()

	run(url, apikey, secret)
