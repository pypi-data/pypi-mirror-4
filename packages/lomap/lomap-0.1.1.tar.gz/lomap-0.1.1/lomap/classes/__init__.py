import sys
import pkg_resources as pr
import os
import subprocess

# Initialize binaries
if sys.platform[0:5] == 'linux':
	assert(pr.resource_exists('lomap','binaries/linux/ltl2ba'))
	assert(pr.resource_exists('lomap','binaries/linux/scheck2'))
	ltl2ba_binary = pr.resource_filename('lomap','binaries/linux/ltl2ba')
	scheck_binary = pr.resource_filename('lomap','binaries/linux/scheck2')
elif sys.platform == 'darwin':
	assert(pr.resource_exists('lomap','binaries/mac/ltl2ba'))
	assert(pr.resource_exists('lomap','binaries/mac/scheck2'))
	ltl2ba_binary = pr.resource_filename('lomap','binaries/mac/ltl2ba')
	scheck_binary = pr.resource_filename('lomap','binaries/mac/scheck2')
else:
	print '%s platform not supported yet!' % sys.platform
	exit(1)

# Check and fix chmod as needed
if not os.access(ltl2ba_binary, os.X_OK) or not os.access(scheck_binary, os.X_OK):
	try:
		print "You'll be prompted for root password to make some third party binaries executable."
		print "Binaries whose mode will be changed to 755 are:"
		print ltl2ba_binary
		print scheck_binary
		subprocess.Popen(['sudo', 'chmod', '755', ltl2ba_binary, scheck_binary], stdout=subprocess.PIPE, stdin=subprocess.PIPE).communicate()
	except Exception as ex:
		raise Exception(__name__, "Problem setting permissions of binaries: '%s'" % ex)
