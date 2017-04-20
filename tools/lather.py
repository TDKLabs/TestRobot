
import os 
import sys
import re
import glob
import shutil
import optparse
import linecache
import ConfigParser


HOSTS_INI = "hosts.ini"

parser = optparse.OptionParser(usage="Usage: %prog [options] soapui_project.xml")
parser.add_option("-j", "--dev-jboss", action="store", type="string", dest="dev_jboss", help="hostname / IP address mapping for dev-jboss")
parser.add_option("-o", "--dev-oracle", action="store", type="string", dest="dev_oracle", help="hostname / IP address mapping for dev-oracle")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose mode")

group = optparse.OptionGroup(parser, "Alternate option", "For the lazy - Put dev-jboss, dev-oracle into a separate ini. Each under its own heading [JBOSS],[ORACLE]. Declare dev-jboss, dev-oracle and their corresponding IP addresses as key/value pair.")
group.add_option("-i", "--hosts", dest="hosts", metavar="hosts.ini", type="string", help="hosts.ini file to use")
parser.add_option_group(group)

(options, args) = parser.parse_args()
args = list(set(args))


if len(sys.argv)==1 or sys.argv[1]=="-h" or sys.argv[1]=="--help": 
	parser.print_help()
	sys.exit(1)

# hosts.ini not explicitly specified in command line param. this file is special, so load it if it exists in current dir as the default behavior
if options.dev_jboss==None and options.dev_oracle==None and options.hosts==None and os.path.exists(os.path.join(os.getcwd(), HOSTS_INI)):
	options.hosts = HOSTS_INI
	
if (options.dev_jboss==None or options.dev_oracle==None) and (options.hosts==None):
	print " !!! WARNING: You have chosen not to replace hostname tokens in soapui xml. No hostname to ip address translations will be done !!! "
	
if options.verbose:	
	print " options: %s" % str(options)
	print " args:    %s" % str(args)

	
search_regex = "^TC[0-9a-zA-Z_]*\.xml$"

if len(args) == 0: 
	sys.stderr.write("XXX Fatal Error: Missing soapui project xml file name or suite directory. XXX\n")
	sys.exit(1)
	
axmls = []

if options.hosts!=None: 
	config = ConfigParser.ConfigParser(); config.read(options.hosts)
	sectionnames = {'JBOSS':'dev-jboss','ORACLE':'dev-oracle'}
	if not all(map(config.has_section, sectionnames.keys())): 
		sys.stderr.write("XXX Fatal Error: %s is missing a required section. Both JBOSS and ORACLE sections must be present. XXX\n" % HOSTS_INI)
		sys.exit(1)
	l = [ (sectionnames[i],config.get(i,sectionnames[i],None)) for i in sectionnames.keys() if config.get(i,sectionnames[i])!='' ]
else:
	hostnames = {'dev_jboss':'dev-jboss', 'dev_oracle':'dev-oracle'}
	l = [ (hostnames[i],options.__dict__[i]) for i in hostnames.keys() if options.__dict__[i]!=None ]


for arg in args:
	if options.verbose: print "arg: ", arg

	if not os.path.exists(arg): 
		sys.stderr.write("XXX Fatal Error: Cannot find [%s] XXX\n" % arg)
		sys.exit(1)

	if os.path.isdir(arg) and os.getcwd()==os.path.abspath(arg):
		# only glob TC*.xml files in current directory
		args.extend(glob.glob("TC*.xml"))

	elif os.path.isfile(arg):
		if re.compile(search_regex, re.I).search(arg) and "soapui-project" in linecache.getline(arg,2): 
			print "  #### Found soapui project xml: ", arg 
			if len(l)==0: 
				axml = os.path.splitext(arg)[:-1][0] + '.axml'
				shutil.copy(arg, axml)
				axmls.append(axml.replace('"',''))
				continue
			cmd = ["sed","-r"]
			for (k,v) in l:
				cmd.append("-e")
				cmd.append('"')
				cmd.append("s_%s_%s_g"%(k,v))
				cmd.append('"')
			cmd.append('"%s"' % arg)
			cmd.append('>')
			axml = '"' + os.path.splitext(arg)[:-1][0] + '.axml' + '"'
			axmls.append(axml.replace('"',''))
			cmd.append(axml)
			cmd = " ".join(cmd)
			if options.verbose: print cmd	
			os.system(cmd)
		else:
			sys.stderr.write(" XXX lather will no longer process soapui xml files that do not begin with 'TC*.xml' XXX \n")
			sys.exit(1)
		
	else:
		# all others
		sys.stderr.write("XXX Fatal Error: Cannot determine [%s] XXX\n" % arg)
		sys.exit(1)
	

print "[axmls]:"
print "+---------------------------------------------------+"
map(lambda x: sys.stdout.write("  (%d):	%s\n"%(x[0],x[1])), list(enumerate(axmls,1)))
print "+---------------------------------------------------+"
if not axmls: sys.exit(0) 

axmls = map(lambda x: '"%s"'%x, axmls)

if sys.platform.startswith("linux"):
	open('AXML.sh','w').write("export %s=%s" % ("AXML",",".join(axmls)))
else:
	open('AXML.bat','w').write("set %s=%s" % ("AXML"," ".join(axmls)))

if all(map(lambda x: os.path.exists(x.replace('"','')), axmls)):
	print " ... Done lather'ing."	
	sys.exit(0)
else:
	sys.stderr.write("XXX Fatal Error: Cannot find generated axml file(s) XXX")
	sys.exit(1)
