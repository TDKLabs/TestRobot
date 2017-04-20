from optestplusplus import *
import re, os

dirs = sys.argv[1:]

search_regex = "^TC[0-9]+\.py$"

files = []
modules = []
for i in dirs:
	for r,d,f in os.walk(i):
		f = filter(re.compile(search_regex, re.I).search, f)
		if f: 
			modules.append(r)
			files.extend(f)

moduleNames = map(lambda f: os.path.splitext(f)[0], filter(re.compile(search_regex,re.I).search,files))
print "  Found the following test script(s): "
for l in enumerate(files,1): print "   @@@ (%d) [%s] @@@ " % (l[0],l[1])

#map(lambda x: sys.stdout.write("  @@@ (%d) Found the following test script: [%s] @@@ \n" % (x[0],x[1])),enumerate(files,1))
#print "files: ", files, " module dirs: ", modules, " moduleNames: ", moduleNames

sys.path.extend(modules)
loader = unittest.TestLoader()
modules = map(loader.loadTestsFromModule, map(__import__, moduleNames))

#print "modules: ", modules
def _x_(m):
	if m._tests:
		for r in m._tests:
			for s in r._tests: 
				if str(s) == "runTest (optestplusplus.WebBaseTest)": r._tests.remove(s)
	return m
modules = map(_x_, modules)
#print "Modules: ", modules

results = HTMLTestRunner.HTMLTestRunner(
		stream = open("results/report.html", "w"),
		title = 'Selenium Test Report',
		verbosity = 2,
		description = 'Selenium Test Execution Report'
		).run(unittest.TestSuite(modules)).result

exit(1) if any(map(lambda x: x[0], results)) else exit(0)

