#
# TDK Test Case Loader Library
#

import sys
from robot.api import logger


logger.debug(" ... Importing tdk_testloader library ... ")

class tdk_testloader:

    def __init__(self):
        logger.debug(" ... in tdk_testloader constructor ... ")
            
    def run_pybot(self, tcfile=None):
        logger.debug(" ... in tdk_testloader.run_OpTest running [%s] ... " % tcfile)
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")
        import os
        from robot import run
        rc = run(tcfile, loglevel=os.getenv('ROBOT_SYSLOG_LEVEL'), outputdir=os.getenv('ROBOT_REPORTDIR'), debugfile=os.getenv('ROBOT_DEBUGFILE'))
        assert rc == 0
        return rc		

    def run_pytest(self, tcfile=None, debug=False):
        logger.debug(" ... in tdk_testloader.run_OpTestPlusplus running [%s] ... " % tcfile)
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")
        import pytest
        # pytest will return 0 as all tests passed, 1 if any tests failed
        rc = pytest.main(["-s","-v", tcfile] if not debug else ["-s","-v","--pdb", tcfile])
        assert rc == 0
        return rc

    def run_makesuds(self, tcfile=None):
        logger.debug(" ... in tdk_testloader.run_SoapUI running [%s] ... " % tcfile)
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")
        
        import subprocess
        from tdk import HOST, ORACLE
        p = subprocess.Popen("makesuds -v %s %s" % (("-j %s "%(HOST if HOST else "")+("-o %s "%(ORACLE if ORACLE else "")),tcfile)), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        map(lambda x: sys.stdout.write(x), iter(p.stdout.readline,""))
        rc = p.wait()
        #soapui return code means nothing. you still have to verify by grep'ing error logs.
        
        if rc==None: return 0
        else: return rc
        
    def run_jrunner(self, tcfile=None): 
        logger.debug(" ... in tdk_testloader.run_jrunner running [%s] ... " % tcfile)
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")
       
        import subprocess
        from tdk import MQ_ENV
        p = subprocess.Popen("jrunner --env %s %s" % (MQ_ENV,tcfile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        map(lambda x: sys.stdout.write(x), iter(p.stdout.readline,""))
        rc = p.wait()
        
        assert rc == 0
        return rc
    
    def run_antrunner(self, tcfile=None): 
        logger.debug(" ... in tdk_testloader.run_antrunner running [%s] ... " % tcfile)
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")
       
        import subprocess
        p = subprocess.Popen("antrunner -f %s" % (tcfile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        map(lambda x: sys.stdout.write(x), iter(p.stdout.readline,""))
        rc = p.wait()
        
        assert rc == 0
        return rc

    def run_mvnrunner(self, tcfile=None): 
        logger.debug(" ... in tdk_testloader.run_mvnrunner running [%s] ... " % tcfile)
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")
       
        import subprocess
        from  tdk import HADOOP_ENV
        from tdk import ENV
        if tcfile == "pom":
            p = subprocess.Popen("mvnrunner -Dxunit.tc.name=%s -DatkEnvModule=%s" % (tcfile, ENV), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        elif tcfile.endswith("testNG"):
            logger.debug(" ... in mvnrunner ... ")
            p = subprocess.Popen("mvnrunner -DsuiteFile=%s -DatkEnvModule=%s" % (tcfile+".xml", ENV), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            p = subprocess.Popen("mvnrunner -DHadoopEnv=%s -Dtest=%s -Dxunit.tc.name=%s -DatkEnvModule=%s" % (HADOOP_ENV, tcfile, tcfile, ENV), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        map(lambda x: sys.stdout.write(x), iter(p.stdout.readline,""))
        rc = p.wait()
        
        assert rc == 0
        return rc

    def run_protractorrunner(self, tcfile=None):
        logger.debug(" ... in tdk_testloader.run_protractorrunner running [%s] ... " % tcfile)
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")
        
        import subprocess
        p = subprocess.Popen("protractor_runner %s" % (tcfile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        map(lambda x: sys.stdout.write(x), iter(p.stdout.readline,""))
        rc = p.wait()
        
        assert rc == 0
        return rc

    def run_rubyrunner(self, tcfile=None):
        logger.debug(" ... in tdk_testloader.run_rubyrunner running [%s] ... " % tcfile)
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")

        import subprocess
        p = subprocess.Popen("ruby_runner %s" % (tcfile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        map(lambda x: sys.stdout.write(x), iter(p.stdout.readline,""))
        rc = p.wait()

        assert rc == 0
        return rc
        
    def run_container(self, tcfile=None):
        logger.debug(" ... in tdk_testloader.run_Container ... ")
        if tcfile==None: raise UnboundLocalError("Test case file name not defined!")
