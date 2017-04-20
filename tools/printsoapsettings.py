import os
import sys
import xml
from xml.etree import ElementTree

if len(sys.argv) == 1:
	print "usage: %s <soapui-settings.xml>" % (os.path.basename(__file__))
	sys.exit(1)
		
tree = ElementTree.parse(sys.argv[1])
root = tree.getroot()

node = root.find('.//*[@id="WSISettings@location"]')
print "WSISettings@location: [", node.text, "]"

node = root.find('.//*[@id="SSLSettings@keyStore"]')
print "SSLSettings@keyStore: [", node.text, "]"

node = root.find('.//*[@id="SSLSettings@keyStorePassword"]')
print "SSLSettings@keyStorePassword: [", node.text, "]"