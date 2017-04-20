
#
# TODO: Add prerun & postrun callback hooks, pytest debugger integration, component and their dependencies, runlist filtering options - wildcards, etc.
#
# Integrated tdkrunner for running any of the supported testscript files: OpTest, OpTest++, SoapUI, or 
# generic container type containing any of the above listed test types.
#

import os, sys, glob, string, subprocess, time, re, socket, datetime
import ConfigParser
import fnmatch
from optparse import OptionParser, OptionGroup
from Timer import Timer
from hurry.filesize import size


# *** Special variables for AHP use only ***
HOST = os.getenv('JBOSSHOST',None)
PORT = os.getenv('JBOSSPORT','8080')
ORACLE = os.getenv('ORACLE',None)

DB_USER = os.getenv('DB_USER',None)
DB_PASSWORD = os.getenv('DB_PASSWORD',None)
DB_PORT = os.getenv('DB_PORT',None)
DB_SID = os.getenv('DB_SID',None)
DB_SERVICE = os.getenv('DB_SERVICE',None)
DB_CONNECTOR = os.getenv('DB_CONNECTOR',None)
MQ_ENV = os.getenv('MQ_ENV',None)
HADOOP_ENV= os.getenv('HADOOP_ENV', None)
# *** End of special variables ***


print "sys.argv = ", sys.argv
CWD = os.getcwd()
if sys.platform.startswith("linux"):
	print "@@@ [uid: %s] [script: %s] [pwd: %s] [host: %s] @@@" % (os.getuid(), sys.argv[0], CWD, os.popen("ifconfig | grep -A 2 'eth' | grep 'inet addr:' | cut -d':' -f2 | awk '{print $1}'").read().strip())


# optionparser cb
def vararg_cb(option, opt_str, value, parser):
	assert value is None
	value = []
	for arg in parser.rargs:
		if arg[:2]=="--" and len(arg)>2: break
		value.append(arg)
	del parser.rargs[:len(value)]
	setattr(parser.values, option.dest, value)
	
parse = OptionParser(usage="Usage: %prog [options] test_script [test_scripts]")
parse.add_option("--dry-run", action="store_true", dest="dryrun", default=False, help="dry run mode - Don't actually do it, just pretend and go through the motions.")
parse.add_option("--env", action="store", dest="env", type="string", metavar="[DEV|QA|IQA|STAGE|TEAM]", help="which deployment environment to run in - Must be one of [DEV|QA|IQA|STAGE|TEAM]. See TestROBOT/conf/env.ini for more info on the different env options.")
parse.add_option("--tag", dest="tag", metavar="[BVT|BAT|IINT|EINT|EBVT|FUN|REG|SMK|MLTB]", action="callback", callback=vararg_cb, help="which tag or collection of tags to run - Can be supplied as a single parameter or as multiple pararmeters. [BVT BAT IINT EINT EBVT FUN REG SMK MLTB]. To run only a single tag e.g. --tag BVT; to run a union of tags, supply the tags separated by space e.g. to run with all tags: --tag BAT BVT IINT EINT EBVT FUN REG SMK MLTB")
parse.add_option("--component", dest="comp", action="callback", callback=vararg_cb, help="which component's TC to run. See TestROBOT/conf/svn.ini for more info on the different Component/Module options.")
parse.add_option("--ie", action="store_true", dest="ie", default=False, help="Use IE WebDriver. This will launch IE instead of the default Firefox.")
parse.add_option("--chrome", action="store_true", dest="chrome", default=False, help="Use Chrome WebDriver. This will launch Chrome instead of the default Firefox.")
parse.add_option("--safari", action="store_true", dest="safari", default=False, help="Use Safari WebDriver. This will launch Safari instead of the default Firefox.")
parse.add_option("--phantomjs", action="store_true", dest="phantom", default=False, help="Use PhantomJS WebDriver. This will launch PhantomJS instead of the default Firefox.")
parse.add_option("--system-test", action="store_true", dest="system_test", default=False, help="System test mode. This will disable all pre-run checks.")

group = OptionGroup(parse, "Debug options")
group.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="Break into python debugger on first fail.")
group.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose mode.")
group.add_option("-b", "--batch", action="store_true", dest="batch", default=False, help="RobotFramework batch mode.")
group.add_option("-r", "--runlist", action="store", dest="runlist", metavar="[runlist file]", type="string", help="Seed runlist with tc list from file.")
group.add_option("-p", "--pause", action="store", dest="pause", type="string", metavar="[secs pause]", default="0.0", help="Pause in seconds in between each run. [Default set to 0.0s]")
group.add_option("-n", action="store", dest="first", type="int", default=None, help="First n number of TC in set to run. E.g. to run the first 5 TC in runlist, use -n 5")
group.add_option("-f", action="store", dest="env_file", type="string", default=None, help="Env file to use. E.g. to use an alternate env file, -f /path/to/my/env.ini. See TestROBOT/conf/env.ini for file format specifics.")
group.add_option("-R", action="store_true", dest="rand", default=False, help="Randomize tc list.")
group.add_option("-N", action="store", dest="num_processes", type="int", default=1, help="# of parallel processes (SMP). E.g. to spawn 4 parallel processes: use -N 4")

parse.add_option_group(group)

if len(sys.argv)==1 or sys.argv[0]=='-h' or sys.argv[0]=='--help' or sys.argv[0]=='-help': 
	parse.print_help()
	sys.exit(1)

(options,args) = parse.parse_args()
if options.verbose:
	print " => options: %s" % str(options) 
	print " => args:    %s" % str(args)

###############################################################


if options.comp != None:
	print " => chdir to %s " % os.path.join(CWD,options.comp[0])
	os.chdir(os.path.join(CWD,options.comp[0]))


import tdk
if options.ie or options.safari:
	if sys.platform != "win32":
		sys.stderr.write("!!! WARN: You selected to run IE on a non-Windows platform. Defaulting to Firefox !!!\n")
	else:	
		if options.ie:
			print " => Using IE Webdriver"
			tdk.BROWSER = 'Ie'
		elif options.safari:
			print " => Using Safari Webdriver"
			tdk.BROWSER = 'Safari'
elif options.chrome:
	print " => Using Chrome Webdriver"
	tdk.BROWSER = 'Chrome'
elif options.phantom:
	print " => Using PhantomJS Webdriver"
	tdk.BROWSER = 'PhantomJS'
else:
	print " => Using default Firefox Webdriver"
import sst.config
sst.config.browser_type = tdk.BROWSER



# --- 8< ---- --- 8< ---- --- 8< ---- --- 8< ---- --- 8< ----
import tdk
tdk.HOST = HOST
tdk.PORT = PORT
tdk.ORACLE = ORACLE
tdk.DB_USER = DB_USER
tdk.DB_PASSWORD = DB_PASSWORD
tdk.DB_PORT = DB_PORT
tdk.DB_SID = DB_SID
tdk.DB_SERVICE = DB_SERVICE
tdk.DB_CONNECTOR = DB_CONNECTOR
tdk.ENV = None
tdk.MQ_ENV = MQ_ENV
# --- 8< ---- --- 8< ---- --- 8< ---- --- 8< ---- --- 8< ----



BUILDINFO_STR = None
'''
try:
	subprocess.check_output(["get_buildinfo",HOST,PORT], shell=False if sys.platform.startswith("linux") else True)
except:
	pass

BUILDINFO = "BUILDINFO.TestROBOT"
def write_buildinfo_file():
	BUILDINFO_STR = subprocess.check_output(["get_buildinfo",HOST,PORT], shell=False if sys.platform.startswith("linux") else True)
	open(BUILDINFO,"w").write(BUILDINFO_STR + '\n')
	
RUNLIST_FILE = "RUNLIST.TestROBOT"
def write_runlist_file(l):
	open(RUNLIST_FILE,"w").write('\n'.join(l) + '\n')
'''
	
	
def seed_sequence_list(l):
	# TODO: Use itertools. ts section to define how this seeding will happen. For now, just randomize.
	#import random
	#random.shuffle(l)
	
	# TODO: n:m
	if options.first:
		l = l[:options.first]
	return l

def generate_runlist(l):
    r = []
    files = []
    for (seq, tc) in enumerate(l, 1):
    # from testcase name get actual testcase file (filename). testcase = testcase file - file extension
        files = glob.glob(tc + "*")
        files = sorted(files)
        # if files are empty, TestROBOT look for tc file (.java only) in all subdirectories
        if files == []:
            found = False
            if os.path.splitext(tc)[1] == ".java":
                tc_re = tc
            else:
                # look only for .java files because TestROBOT don't allow other types in subdirectories
                tc_re = tc + ".java"
            for root, dirs, filenames in os.walk("."):
                for filename in fnmatch.filter(filenames, tc_re):
                    # TestROBOT don't support container functionality for Java yet
                    files.append(tc_re)
                    found = True
                    break
                # caring about first occurance since TC with same name created in multiple locations/packages isn't encouraged
                if (found):
                    break

        # check to make sure TC file(s) actually exists and match the TC in runlist
        if len(files)==0:
            sys.stderr.write("!!! WARN: Can't find TC: %s in current dir: %s !!!\n" % (tc,os.getcwd()))
            continue

        filename = files[0] # container is always first after sorting

        # if multiple TC files found, need to make sure container file exists
        if len(files) > 1:
            if options.verbose: print " [%s] => glob(TC*) returned => %s " % (tc, str(files))

            if os.path.splitext(filename)[-1] != '':
                print "!!! WARN: Inconsistency in TC detected. It appears that you have multiple files for TC (%s) but no container for it. Perhaps you're missing the container file? Skipping !!!" % (
                tc)
                continue
        print "	@@@ (%d) [%s] @@@ " % (seq, filename)
        r.append(create_runner(filename))
    return r

	
import tdk_testloader
loader = tdk_testloader.tdk_testloader()
	
def create_runner(file):
	(name,ext) = os.path.splitext(file)
	if options.system_test:
		# XXX '_' is special. will be delimiter for multiple TC's in same container.
		if "_" in name:
			name = name.split("_")[0]

	if ext == ".txt":
		return OpTestRunner(name, file)
	elif ext == ".py":
		return OpTestPlusPlusRunner(name, file)
	elif name.startswith("build") and ext == ".xml":
		return AntRunner(name, file)
	elif (name == "pom" and ext == ".xml") or (ext == ".java"):
		return MvnRunner(name, file)
	elif name.endswith("testNG") and ext == ".xml":
		return MvnRunner(name, file)
	elif ext == ".xml":
		return SoapUIRunner(name, file)
	elif ext == ".groovy":
		return OpTestJRunner(name, file)
	elif ext == ".js":
		return ProtractorRunner(name, file) 
	elif ext == ".rb":
		return RubyRunner(name, file) 
	elif ext == "":
		return ContainerRunner(name, file)
	else:
		raise NotImplementedError("No runner found for this file type.")

class AbstractRunner(object):
	def __init__(self, name, file):
		self.name = name
		self.file = file
		self.seq = 0
		
	def __str__(self):
		return "#%d. [%s (%s)] => [%s]"%(self.seq,self.file,self.name,self.__class__.__name__)
		
	def run(self):
		raise NotImplementedError
	
	
from functools import wraps
def run(s):
	@wraps(s)
	def wrapper(*args):
		if options.system_test and "_" in args[0].name: 
			args[0].name = args[0].name.split("_")[0]
		args[0].seq = [ i.name for i in runlist ].index(args[0].name)+1
		status = " [%d / %d] " % (args[0].seq, len(runlist))
		pad = (78-len(status))/2
		print "%s%s%s" % ("<"*pad,status,">"*pad)
		
		if options.pause and float(options.pause): 
			if options.verbose: 
				print " ... sleeping for %s s between runs ... " % options.pause
			time.sleep(float(options.pause))
		with Timer() as t:
			result = s(*args)
		status = " [%s] " % (str(datetime.timedelta(seconds=t.secs)))
		pad = (78-len(status))/2
		print "%s%s%s" % (">"*pad,status,"<"*pad) 

		return result
	return wrapper
	
class OpTestRunner(AbstractRunner):
	def __init__(self, name, file):
		AbstractRunner.__init__(self, name, file)
		
	@run	
	def run(self):
		if options.verbose: print " @@@ in optestrunner (%s) @@@ " % self.file	

		rc = 0
		if not options.batch:
			# FIXME: 
			os.putenv('DB_PROPERTIES',db_prop)
			try:
				rc = loader.run_pybot(self.file)
			except AssertionError: 
				rc = 1
				
		else:
			from robot.api import TestSuite, TestSuiteBuilder
			suite = TestSuite(str(self))
			suite.imports.resource("optest_common_resource.txt")
			suite.imports.library("tdk_testloader")
			t = suite.tests.create(name=self.name)
			t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
			t.keywords.create("Run Pybot", args=[self.file])			
			rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'),self.name))
			#debugfile=os.getenv('ROBOT_DEBUGFILE')
			rc = rc.return_code		
		return rc
	
class OpTestPlusPlusRunner(AbstractRunner):
	def __init__(self, name, file):
		AbstractRunner.__init__(self, name, file)
		
	@run	
	def run(self):
		if options.verbose: print " @@@ in optestplusplusrunner (%s) @@@ " % self.file

		rc = 0
		if not options.batch:
			# FIXME: 
			os.putenv('DB_PROPERTIES',db_prop)
			try:
				rc = loader.run_pytest(self.file, debug=options.debug)
			except AssertionError:
				rc = 1
				
		else:
			from robot.api import TestSuite, TestSuiteBuilder
			suite = TestSuite(str(self))
			suite.imports.resource("optest_common_resource.txt")
			suite.imports.library("tdk_testloader")
			t = suite.tests.create(name=self.name)
			t.keywords.create("Set Environment Variable", args=["SCREENSHOT_DIR",os.getenv('ROBOT_REPORTDIR')+'/'+'SEL-SCREENSHOTS'])
			t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
			t.keywords.create("Run Pytest", args=[self.file])			
			rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'),self.name))
			#debugfile=os.getenv('ROBOT_DEBUGFILE')
			rc = rc.return_code		
		return rc
			
class SoapUIRunner(AbstractRunner):
	def __init__(self, name, file):
		AbstractRunner.__init__(self, name, file)
		
	@run	
	def run(self):		
		if options.verbose: print " @@@ in soapuirunner (%s) @@@ " % self.file
		
		rc = 0
		if not options.batch:
			# FIXME: 
			os.putenv('DB_PROPERTIES',db_prop)
			rc = loader.run_makesuds(self.file)
			
		else:
			from robot.api import TestSuite, TestSuiteBuilder
			suite = TestSuite(str(self))
			suite.imports.resource("optest_common_resource.txt")
			suite.imports.library("tdk_testloader")
			t = suite.tests.create(name=self.name)
			t.keywords.create("Set Environment Variable", args=["NO_SOAPUI_REPORT","1"])
			t.keywords.create("Set Environment Variable", args=["SOAPUI_LOGSDIR",os.getenv('ROBOT_REPORTDIR')+'/'+self.name+'/'+'SOAPUI_LOGS'])
			t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
			t.keywords.create("Run Makesuds", args=[self.file])
			t.keywords.create("Soapui Project Passed", args=[os.getenv('ROBOT_REPORTDIR')+'/'+self.name+'/'+'SOAPUI_LOGS/soapui-errors.log']) # dirty hack since create doesn't expand vars
			rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'),self.name))
			#debugfile=os.getenv('ROBOT_DEBUGFILE')
			rc = rc.return_code		
		return rc		

class OpTestJRunner(AbstractRunner):
	def __init__(self, name, file):
		AbstractRunner.__init__(self, name, file)
		
	@run	
	def run(self):
		if options.verbose: print " @@@ in optestjrunner (%s) @@@ " % self.file	

		rc = 0
		if not options.batch:
			# FIXME: 
			os.putenv('DB_PROPERTIES',db_prop)
			try:
				rc = loader.run_jrunner(self.file)
			except AssertionError: 
				rc = 1
				
		else:
			from robot.api import TestSuite, TestSuiteBuilder
			suite = TestSuite(str(self))
			suite.imports.resource("optest_common_resource.txt")
			suite.imports.library("tdk_testloader")
			t = suite.tests.create(name=self.name)
			t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
			t.keywords.create("Run JRunner", args=[self.file])			
			rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'),self.name))
			#debugfile=os.getenv('ROBOT_DEBUGFILE')
			rc = rc.return_code		
		return rc
	
class AntRunner(AbstractRunner):
	def __init__(self, name, file):
		AbstractRunner.__init__(self, name, file)
		
	@run	
	def run(self):
		if options.verbose: print " @@@ in antrunner (%s) @@@ " % self.file	

		rc = 0
		if not options.batch:
			# FIXME: 
			os.putenv('DB_PROPERTIES',db_prop)
			try:
				rc = loader.run_antrunner(self.file)
			except AssertionError: 
				rc = 1
				
		else:
			from robot.api import TestSuite, TestSuiteBuilder
			suite = TestSuite(str(self))
			suite.imports.resource("optest_common_resource.txt")
			suite.imports.library("tdk_testloader")
			t = suite.tests.create(name=self.name)
			t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
			t.keywords.create("Run AntRunner", args=[self.file])			
			rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'),self.name))
			#debugfile=os.getenv('ROBOT_DEBUGFILE')
			rc = rc.return_code		
		return rc	

class MvnRunner(AbstractRunner):
    def __init__(self, name, file):
        AbstractRunner.__init__(self, name, file)

    @run
    def run(self):
        if options.verbose: print " @@@ in mvnrunner (%s) @@@ " % self.file

        rc = 0
        if not options.batch:
            # FIXME:
            os.putenv('DB_PROPERTIES', db_prop)
            try:
                rc = loader.run_mvnrunner(self.file)
            except AssertionError:
                rc = 1

        else:
            from robot.api import TestSuite, TestSuiteBuilder

            suite = TestSuite(str(self))
            suite.imports.resource("optest_common_resource.txt")
            suite.imports.library("tdk_testloader")
            t = suite.tests.create(name=self.name)
            t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES", db_prop])
            t.keywords.create("Run MvnRunner", args=[self.name])
            rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'),
                           outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'), self.name))
            # debugfile=os.getenv('ROBOT_DEBUGFILE')
            rc = rc.return_code
        return rc

class ProtractorRunner(AbstractRunner):
	def __init__(self, name, file):
		AbstractRunner.__init__(self, name, file)
		
	@run	
	def run(self):
		if options.verbose: print " @@@ in protractorrunner (%s) @@@ " % self.file	

		rc = 0
		if not options.batch:
			# FIXME: 
			os.putenv('DB_PROPERTIES',db_prop)
			try:
				rc = loader.run_protractorrunner(self.file)
			except AssertionError: 
				rc = 1
				
		else:
			from robot.api import TestSuite, TestSuiteBuilder
			suite = TestSuite(str(self))
			suite.imports.resource("optest_common_resource.txt")
			suite.imports.library("tdk_testloader")
			t = suite.tests.create(name=self.name)
			t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
			t.keywords.create("Run ProtractorRunner", args=[self.file])			
			rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'),self.name))
			#debugfile=os.getenv('ROBOT_DEBUGFILE')
			rc = rc.return_code		
		return rc	

class RubyRunner(AbstractRunner):
        def __init__(self, name, file):
                AbstractRunner.__init__(self, name, file)

        @run
        def run(self):
                if options.verbose: print " @@@ in rubyrunner (%s) @@@ " % self.file 

                rc = 0
                if not options.batch:
                        # FIXME: 
                        os.putenv('DB_PROPERTIES',db_prop)
                        try:
                                rc = loader.run_rubyrunner(self.file)
                        except AssertionError:
                                rc = 1

                else:
                        from robot.api import TestSuite, TestSuiteBuilder
                        suite = TestSuite(str(self))
                        suite.imports.resource("optest_common_resource.txt")
                        suite.imports.library("tdk_testloader")
                        t = suite.tests.create(name=self.name)
                        t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
                        t.keywords.create("Run RubyRunner", args=[self.file])        
                        rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'),self.name))
                        #debugfile=os.getenv('ROBOT_DEBUGFILE')
                        rc = rc.return_code
                return rc

class ContainerRunner(AbstractRunner):
	# TODO: add prop xfer from one step to the next

	def __init__(self, name, file):		
		AbstractRunner.__init__(self, name, file)
		lines = open(file).read().split()
		if not all(map(lambda l: os.path.splitext(l)[0].startswith(name), lines)): 
			if not options.system_test:
				sys.stderr.write(" XXX Serious Error: TestCase (%s) contains sub-testcase(s) that do not belong to it. Please double check contents of this TC! XXX \n " % name)
				sys.exit(1)
		self.runners = map(lambda l: create_runner(l), lines)
	
	@run
	def run(self):
		if options.verbose: print " @@@ in containerrunner (%s) @@@ " % self.file	
		
		rc = 0
		if not options.batch:
			for r in self.runners:
				if r.run()==1: 
					rc=1
					break # bail out if previous step failed! container structure has to be a single contiguous unit of execution

		else:
			from robot.running import TestSuite, TestSuiteBuilder
			suite = TestSuite(str(self))
			suite.imports.resource("optest_common_resource.txt")
			suite.imports.library("tdk_testloader")
			t = suite.tests.create(name=self.name)
			
			for r in self.runners:
				if isinstance(r,OpTestRunner):
					t.keywords.create("Run Pybot", args=[r.file])	
					t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
				
				elif isinstance(r,OpTestPlusPlusRunner):
					t.keywords.create("Set Environment Variable", args=["SCREENSHOT_DIR",os.getenv('ROBOT_REPORTDIR')+'/'+'SEL-SCREENSHOTS'])
					t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
					t.keywords.create("Run Pytest", args=[r.file])
				
				elif isinstance(r,SoapUIRunner):
					t.keywords.create("Set Environment Variable", args=["NO_SOAPUI_REPORT","1"])
					t.keywords.create("Set Environment Variable", args=["SOAPUI_LOGSDIR",os.getenv('ROBOT_REPORTDIR')+'/'+r.name+'/'+'SOAPUI_LOGS'])
					t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
					t.keywords.create("Run Makesuds", args=[r.file])
					t.keywords.create("Soapui Project Passed", args=[os.getenv('ROBOT_REPORTDIR')+'/'+r.name+'/'+'SOAPUI_LOGS/soapui-errors.log']) # dirty hack since create doesn't expand vars
					
				elif isinstance(r,OpTestJRunner):
					t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
					t.keywords.create("Run JRunner", args=[r.file])

				elif isinstance(r,MvnRunner):
					t.keywords.create("Set Environment Variable", args=["DB_PROPERTIES",db_prop])
					t.keywords.create("Run MvnRunner", args=[r.file])
			
			rc = suite.run(loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.path.join(os.getenv('ROBOT_REPORTDIR'),r.name)) #debugfile=os.getenv('ROBOT_DEBUGFILE') XXX not working ???
			rc = rc.return_code		
		return rc	

###############################################################

# run list containing different Runner instances	
runlist = []
# list of chars to escape in dbPassword string in windows
char_esc_win_list = ['^', '&', '<', '>', '|', ')', '(']


'''
# scrape buildinfo from buildinfo_service so we know what exactly we're hitting
#write_buildinfo_file()
print " *************************"
print " **** BUILD INFO [%s] ****" % BUILDINFO_STR
print " *************************"
'''

# environment specific setup
# There are 2 types of env - team (Product module), shared (Suite)
# TODO: env properties override cli or vice versa
db_prop = ""
if options.env != None:
	### run using specified env ###
	ENV_INI = options.env_file if options.env_file else os.path.join(os.getenv('TROBOT'),"conf","env.ini")

	if not os.path.exists(ENV_INI):
		sys.stderr.write(" XXX Fatal Error: ENV_INI - %s not found. XXX\n " % ENV_INI)
		sys.exit(1)
		
	config = ConfigParser.ConfigParser()
	config.optionxform = str
	config.read(ENV_INI)
	
	# get tclist: this can be either specified via --tag parameter or via env.ini tag ini variable 
	for sect in config.sections():
		def _find_(K,V):
			s=re.compile('\[(.*?)\]').search(V)
			if s: 
				V=V.replace(s.group(), config.get(s.group(1), K))
				_find_(K,V)
			return V
	
		for (k,v) in config.items(sect):
			if k == "dbPassword":
				#  escaping char '\' in dbPassword string - all environments
				v = v.replace("\\", "\\\\")
				#  escaping a list of chars in dbPassword string - windows only
				if sys.platform == "win32":
					for val in char_esc_win_list:
						v = v.replace(val, "^{}".format(val))
			config.set(sect,k,_find_(k,v))
	
	env_properties = dict(config.items(options.env.upper()))
	
	# FIXME: soapui + py properties to be set here. env to be passed in ??? ...	
	tdk.HOST = env_properties.get('appServer') if not tdk.HOST else tdk.HOST
	tdk.PORT = env_properties.get('appServerPort') if not tdk.PORT else tdk.PORT
	tdk.ORACLE = env_properties.get('dbServer') if not tdk.ORACLE else tdk.ORACLE
	tdk.DB_USER = env_properties.get('dbUser',None)
	tdk.DB_PASSWORD = env_properties.get('dbPassword',None)
	tdk.DB_SID = env_properties.get('dbSid',None)
	tdk.DB_SERVICE = env_properties.get('dbService',None)
	tdk.DB_CONNECTOR = env_properties.get('dbConnector',None)
	tdk.DB_PORT = env_properties.get('dbPort',None)
	tdk.MQ_ENV = env_properties.get('mqEnv',None)
    
	tdk.HADOOP_ENV = env_properties.get('hadoopEnv',None)
	tdk.ENV = options.env
	tdk.LOG_HOST = env_properties.get('logServer',None)
	tdk.LOG_PATH = env_properties.get('logPath',None)
	tdk.LOG_USERNAME = env_properties.get('logUsername',None)
	tdk.LOG_PASSWD = env_properties.get('logPassword',None)
		
	for k,v in { i: env_properties[i] for i in ['dbUser','dbPassword','dbPort'] }.items():
		db_prop = db_prop + " -P%s=%s " % (k,v) 
	if 'testEnv' in env_properties:
		db_prop = db_prop + " -P%s=%s " % ('testEnv',env_properties['testEnv'])
	if 'dbSid' in env_properties:
		db_prop = db_prop + " -P%s=%s " % ('dbSid',env_properties['dbSid'])
	if 'dbService' in env_properties:
		db_prop = db_prop + " -P%s=%s " % ('dbService',env_properties['dbService'])
	if 'dbConnector' in env_properties:
		db_prop = db_prop + " -P%s=%s " % ('dbConnector',env_properties['dbConnector'])
	if 'logServer' in env_properties:
		db_prop = db_prop + " -P%s=%s " % ('logServer',env_properties['logServer'])
	if 'logPath' in env_properties:
		db_prop = db_prop + " -P%s=%s " % ('logPath',env_properties['logPath'])
	if 'logUsername' in env_properties:
		db_prop = db_prop + " -P%s=%s " % ('logUsername',env_properties['logUsername'])
	if 'logPassword' in env_properties:
		db_prop = db_prop + " -P%s=%s " % ('logPassword',env_properties['logPassword'])
	# FIXME: for backward compatibility. Should do away with this hack entirely
	db_prop = "-PdbHost=%s %s" % (ORACLE,db_prop)	
	
	# get set of tags and set to options
	options.tag = options.tag if options.tag else env_properties['tag'].split() if 'tag' in env_properties else None
		
	if options.verbose:
		print " => env_properties: %s" % env_properties
		print " => db_prop: %s" % db_prop


# runlist setup
if options.runlist != None:
	### run in list mode ###
	tclist = open(options.runlist).read().split()
	if options.verbose: print " *** tc running sequence: %s *** " % str(tclist)
	
elif options.tag != None:
	### run in tag mode ###
	TAG_INI = "tag.ini"
	
	if not os.path.exists(TAG_INI):
		sys.stderr.write(" XXX Fatal Error: %s not found. Did you remember to run atk-rally first? XXX\n " % TAG_INI)
		sys.exit(1)
	
	tclist = set()
	tagarray = []
	tagarray = options.tag
	do_intersect = False
	count_tags_intersect = len(tagarray[0].split(','))
	if count_tags_intersect == 1:
	    taglist = map(lambda s: s, options.tag)
	    #taglist = map(lambda s: s.upper(), options.tag)
        else:
	        do_intersect = True
	        taglist = map(lambda s: s.upper(), tagarray[0].split(','))
	temp = set()
	config = ConfigParser.ConfigParser()
	# generate tc list from tags
	config.read(TAG_INI)
	
	for tag in taglist:
		try:
			temp = temp.union(set(config.get(tag, 'tc').split())) #dynamically generated tc list for each tag
		except ConfigParser.NoSectionError as e:
			sys.stderr.write(" *** Error! %s *** \n" % str(e))
        #logic to perform intersection of testcase sets based on tags passed
		if do_intersect:
                    # if temp is not empty, perform intersection from two tags
                    if temp:
                        if not tclist:
                            tclist.update(temp)
                        tclist.intersection_update(temp)  # intersection of test cases
                        temp.clear()
                    # temp is empty implies there are no TCs associated with that tag; so intersection is empty.
                    else:
                        tclist.clear()
                        break

                #logic to perform union of testcase sets
                else:
                        tclist.update(temp)
                        temp.clear()


	if not tclist: 
		sys.stderr.write("!!! WARN: No test cases were found !!! \n")
		sys.exit(0)

	tclist = sorted(list(tclist))
	if options.rand:
		import random
		random.shuffle(tclist)
	if options.verbose: print " *** tc running sequence: %s *** " % str(tclist)	
		
else:
	### run in user-specified file or glob mode ###
	
	tclist = []
	
	for file in args:
		if not os.path.exists(file) and not (".java" in file):
			sys.stderr.write("XXX Error! Can't find the file: [%s] XXX\n" % file)
				
		elif os.path.isdir(file) and os.getcwd()==os.path.abspath(file):
			tclist.extend(list(set(map(lambda x: os.path.splitext(x)[0], glob.glob("TC*")+glob.glob("build*.xml")))))
			
		else:
			tclist.append(file)


# from tclist generate runlist - runlist contains runner object instances 			
if len(tclist)==0: 
	sys.stderr.write(" XXX Fatal Error: tdkrunner was not able to generate TC list. Did you enter valid TC filename(s) or tag proper TC's in rally? XXX\n ")
	sys.exit(0)
	
# validate file names to make sure they conform to naming convention TC[0-9]{5}.py
m = map(re.compile("^TC[0-9]{5}$|^build|^pom$").search, map(lambda x: os.path.splitext(x)[0], tclist))
if not all(m):
	sys.stderr.write(" !!! WARN: TC %s does not meet naming convention. !!!\n " % [ tclist[j] for j in [ i for i in range(len(m)) if not m[i] ] ])
	
# TODO: add sort, randomize, seed sequence in specific order if needed here	
with Timer() as t:
	runlist = generate_runlist(tclist)
if options.verbose:  print " $$$ generate_runlist took: %s $$$ " % (str(datetime.timedelta(seconds=t.secs)))
if len(runlist) != len(tclist):
	sys.stderr.write("!!! WARN: Detected some TC(s) is/are missing from filesystem. Possible reason could be TC exists in Rally but hasn't been automated/implemented yet. !!!\n")
	_ = [ j for j in tclist if j not in [ i.name for i in runlist ] ]
	sys.stderr.write("The following TC's are missing: %s \n" % _)
	sys.stderr.write("!!! Expected: [%d], Present: [%d], Missing: [%d] !!!\n" % (len(tclist),len(runlist),len(_)))
runlist = seed_sequence_list(runlist)

# TODO: 
#write_runlist_file(map(lambda r: r.file, runlist))

# check runlist list
if len(runlist)==0: 
	sys.stderr.write(" XXX Fatal Error: tdkrunner was not able to generate list of TC runner(s). Did you commit TC files into SVN? XXX\n ")
	sys.exit(0)


# now start running	
if options.dryrun:
	# dry-run mode
	_ = [ i.name for i in runlist]
	print "*** The following testscripts will be run => # [%d]:%s ***" % (len(_),_)
	sys.exit(0)
else:
	
	# remove all report dirs first before running
	import shutil
	if options.batch:
		for r,d,f in os.walk(os.getcwd()):
			d = map(lambda x: (lambda y: os.path.join(y,x))(r), filter(re.compile(os.getenv('ROBOT_REPORTDIR'), re.I).search, d))
  			if d:
  				if options.verbose:	print " ... removing %s ... " % d
  				shutil.rmtree(d[0], True)
  	else:
  		if options.verbose:	print " ... removing screenshots dir ... "
  		shutil.rmtree(os.path.join(os.getcwd(),"screenshots"),True)
  		if options.verbose:	print " ... removing soapui_logs dir ... "
  		shutil.rmtree(os.path.join(os.getcwd(),"soapui_logs"),True)


	# TODO: Refactor this 
	import optest, tdk_dbi
	
	if sys.platform.startswith("linux"):
		import signal
		def _handler_(s,f):
			op.stop_display()
			print " !!! Execution was prematurely interrupted. Quitting !!! "
			sys.exit(1)
		signal.signal(signal.SIGTERM, _handler_)
		signal.signal(signal.SIGINT, _handler_)

		from multiprocessing import Process, Manager, log_to_stderr, get_logger
		from operator import itemgetter
		import logging

		MAX_PROCESSES = 8

		_parallel_runlist_ = []
		_dict_ = Manager().dict()
		_workers_ = []
		log_to_stderr()
		logger = get_logger()
		logger.setLevel(logging.INFO)
		
		options.num_processes = MAX_PROCESSES if options.num_processes > MAX_PROCESSES else options.num_processes
		options.num_processes = len(runlist) if options.num_processes > len(runlist) else options.num_processes

		class Worker(Process):
			def run(self):
				os.system("taskset -p 0xff %d" % os.getpid())
				d = self._args[0]
				dbi = tdk_dbi.tdk_dbi()
				dbi.start_jdbc()
				op = optest.optest()
				op.start_display()

				index = int(self.name.split("-")[-1])-2
				if index>=0:
					r = map(lambda r: r.name,_parallel_runlist_[index])
					print " !!! *** parallel runlist index <[%s %s %s]> @@@ run sequence: (%s) *** !!! " % (index, self.name,  os.getenv('DISPLAY'), r)
					rc = map(lambda r: r.run(), _parallel_runlist_[index])
					d[index] = (r, rc)

				op.stop_display()
				return

	with Timer() as t:
		if sys.platform.startswith("linux"):			
			ll = [ i for i,_ in enumerate(runlist) ]
			indices = list(set([ j for j in map(lambda x:x%options.num_processes, ll) ]))			
			_parallel_runlist_ = [ [ runlist[j] for j in ll if (j%options.num_processes)==i ] for i in indices ]
			#print [ [ j for j in ll if (j%options.num_processes)==i ] for i in indices ]
		
			for i in range(options.num_processes):
				_w_ = Worker(args=(_dict_,))
				_workers_.append(_w_)
				_w_.start()			

			map(lambda j: j.join(), _workers_)				

			# flatten dict
			if options.verbose: print " ... parallelized run rc: ", _dict_, " ... "
	
			_dict_ = dict(_dict_)
			def _flatten_(d):
				_ = []
				for i,j in d.itervalues():
					_.extend(zip(i,j))
				return _
			rc = map(lambda x: x[1], sorted(_flatten_(_dict_), key=itemgetter(0)))

		else:
			# pre-run setup		
			dbi = tdk_dbi.tdk_dbi()
			dbi.start_jdbc()
			op = optest.optest()
			op.start_display()			
		
			rc = map(lambda r: r.run(), runlist) 
	
			# post-run teardown
			op.stop_display()
			#dbi.stop_jdbc()
	if options.verbose: print " $$$ setup + run + teardown took: %s $$$ " % (str(datetime.timedelta(seconds=t.secs)))


# post mortem stuff here: robot report + soapui htmls 
if options.batch:
	'''
	rbxml = []
	
	import fnmatch
	for r,d,f in os.walk(os.getenv('ROBOT_REPORTDIR')):
		for xml in f:
			if fnmatch.fnmatch(xml,'output.xml'): 
				rbxml.append(os.path.join(r,xml))
	'''			

	def _find_output_xml_(name):
		xml = glob.glob(os.path.join(os.getenv('ROBOT_REPORTDIR'),"%s*"%name,'output.xml'))
		assert len(xml) > 0
		if len(xml) != 1:
			sys.stderr.write(" !!! WARN: Inconsistency found - (%s) has multiple output.xml [%s] !!! \n" % (name,xml))		
		return xml[0]

	#rbxml = map(lambda r: os.path.join(os.getenv('ROBOT_REPORTDIR'),r,'output.xml'), [ i.name for i in runlist ])
	rbxml = map(_find_output_xml_, [ i.name for i in runlist ])
	if options.verbose: 
		print " => output.xml: ", rbxml
		def _size_(x):
			try:
				return os.stat(x).st_size
			except:
				sys.stderr.write(" !!! WARN: processed TC with non-existent filename: %s !!! \n" % x)
				return 0

		sizes = map(_size_, rbxml)
		print " => sizes: ", sizes
		print " => total: %s" % size(reduce(lambda x,y: x+y, sizes))  
		

	# generate robotfw report and log html
	from robot.api import ResultWriter
	with Timer() as t:
		ResultWriter(*rbxml).write_results( loglevel=os.getenv('ROBOT_SYSLOG_LEVEL')+":INFO", \
                                        name=None if len(rbxml)==1 else '%s Test Suite' % ("" if not getattr(options,'tag',None) else options.tag), \
                                        outputdir=os.getenv('ROBOT_REPORTDIR'), \
                                        logtitle="[JB:%s | OR:%s | COMP:%s | ENV:%s] Test Log" % ("" if not tdk.HOST else tdk.HOST,"" if not tdk.ORACLE else tdk.ORACLE,"" if not getattr(options,'comp',None) else options.comp[0],"" if not getattr(options,'env',None) else options.env), \
                                        reporttitle="[JB:%s | OR:%s | COMP:%s | ENV:%s] Test Report" % ("" if not tdk.HOST else tdk.HOST,"" if not tdk.ORACLE else tdk.ORACLE,"" if not getattr(options,'comp',None) else options.comp[0],"" if not getattr(options,'env',None) else options.env), \
                                        output='combined.xml', \
                                        splitlog=True )
	if options.verbose: print " $$$ ResultWriter.write_results took: %s $$$ " % (str(datetime.timedelta(seconds=t.secs)))

	
	# generate soapui report html
	buildxml = '''\
    <project name="report" default="report" basedir=".">
        <target name="report">
            <mkdir dir="@@"/>
	        <junitreport todir="@@">
                <fileset dir="." includes="**/TEST*.xml"/>
                <report format="frames" todir="@@">
                    <param name="TITLE" expression="SoapUI Test Results."/>
                </report>
            </junitreport>
        </target>
    </project>\
    '''
	buildxml = string.replace(buildxml, "@@", "soapui")
	
	with open(os.path.join(os.getenv('ROBOT_REPORTDIR'), "build.xml"),"w") as f:
		f.write(buildxml)
	
	print " Generating soapui reports. This could take a while ... "
	with Timer() as t:
		os.popen('ant -q -f %s' % os.path.join(os.getenv('ROBOT_REPORTDIR'),'build.xml')).close()
	print " ... done! \n"
	if options.verbose: print " $$$ ant took: %s $$$ " % (str(datetime.timedelta(seconds=t.secs)))
	
	
if options.verbose: 
	print " => rc: ", rc
	print " => runlist: ", [ i.name for i in runlist ]

if any(rc): 
	failed = [ runlist[i].name for i in [ i for i in range(len(rc)) if rc[i] ] ]
	print "=> FAILED ! :( [%03.2f%% fail]|[%d]|%s" % (float(sum(rc))*100/len(runlist),sum(rc),str(failed))
	print '''
      ______
     (( ____ \-
     (( _____
     ((_____
     ((____   ----
          /  /
         (_((

	'''        
	
	sys.exit(1)
else:
	print "=> PASSED ! :)"
	print '''
          _
         /(|
        (  :
       __\  \  _____
     (____)  -|
    (____)|   |
     (____).__|
      (___)__.|_____
    
	'''
	
	sys.exit(0)
			
