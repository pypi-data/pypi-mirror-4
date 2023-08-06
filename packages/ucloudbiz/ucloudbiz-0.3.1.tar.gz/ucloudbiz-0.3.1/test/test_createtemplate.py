#!/usr/bin/env python
from ucloudbiz.server.vm.listvirtualmachines import listVirtualMachines
from ucloudbiz.server.template.createtemplate import createTemplate
from ucloudbiz.server.volume.listvolumes import listVolumes

#########################################################################################
# Reference: 
# http://developer.ucloudbiz.olleh.com/doc/cloudstack/VM/listVirtualMachines/
# http://developer.ucloudbiz.olleh.com/doc/cloudstack/Template/createTemplateA/
#
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


def makeTemplte(virtualmachineid, ostypeid, volumeid):
	displaytext = raw_input("Display Text:")
	name        = raw_input("name:")
	isfeatured  = "true"
	ispublic    = "true"
	passwordenabled = "true"
	requireshvm = "false"
	templatetag = "ktsaas"
	bits        = 64

	logger.debug("Create Template Info")
	logger.debug("displaytext      %s" % displaytext)
	logger.debug("name             %s" % name)
	logger.debug("ostypeid:        %s" % ostypeid)
	logger.debug("bits             %s" % bits)
	logger.debug("isfeatured       %s" % isfeatured)
	logger.debug("ispublic         %s" % ispublic)
	logger.debug("passwordenabled  %s" % passwordenabled)
	logger.debug("requireshvm      %s" % requireshvm)
	logger.debug("templatetag      %s" % templatetag)
	logger.debug("virtualmachineid %s" % virtualmachineid)
	logger.debug("volumeid         %s" % volumeid)

	param = {'displaytext':displaytext,
			'name':name,
			'ostypeid':ostypeid,
			'bits':bits,
			'isfeatured':isfeatured,
			'ispublic':ispublic,
			'passwordenabled':passwordenabled,
			'requireshvm':requireshvm,
			'templatetag':templatetag,
			'virtualmachineid':virtualmachineid,
			'volumeid':volumeid}
	
	return param
	

def run(url, apikey, secret):
	logger.debug("Run API")
	inst = listVirtualMachines(url, apikey, secret)
	volume_inst = listVolumes(url, apikey, secret)

	logger.debug("Filter Stopped VMs")

	param = {'state':'Stopped'}
	result = inst.execute(param)
	dic = inst.parseJsonResult(result)
	response = dic['listvirtualmachinesresponse']
	vms = response['virtualmachine']
	finished = False
	for vm in vms:
		virtualmachineid = vm['id']
		ostypeid = vm['guestosid']

		print "id           %s" % virtualmachineid
		print "guestosid    %s" % ostypeid
		print "templatename %s" % vm['templatename']
		v_param = {'virtualmachineid':virtualmachineid}
		result1 = volume_inst.execute(v_param)
		dic1 = volume_inst.parseJsonResult(result1)
		response1 = dic1['listvolumesresponse']
		volumes = response1['volume']
		for volume in volumes:
			volumeid = volume['id']
			print "volume id   %s" % volumeid
			print "volume name %s" % volume['name']

			yn = raw_input("Create Template(y/n)?>")
			if yn == 'y':
				param = makeTemplte(virtualmachineid, ostypeid, volumeid)
				inst = createTemplate(url, apikey, secret)
				result = inst.execute(param)
				print result
				finished = True
				break
		if finished == True:
			break



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
