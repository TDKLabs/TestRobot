#
# DB Interface Abstraction Library
#

import sys
import os
#import jpype
from robot.api import logger


logger.debug(" ... Importing tdk_dbi library ... ")

class tdk_dbi:

    def __init__(self):
        logger.debug(" ... in tdk_dbi constructor ... ")
            
    def start_jdbc(self):
        # TODO: exact version of ojdbc.jar that needs to be loaded? or any other db drivers
        logger.debug(" ... in tdk_dbi.start_jdbc ... ")
        if sys.platform.startswith('linux'):
	    #jpype.startJVM(os.path.join(os.sep, 'opt','lin','java','latest','jre','lib','i386','client','libjvm.so'), "-Djava.class.path=%s" % os.path.join(os.getenv('TROBOT'), 'libs', 'soapui-4.5.1', 'lib', 'ojdbc5.jar'))
	    pass
        else:
            #jpype.startJVM(os.path.join(os.getenv('TROBOT'),'jre','jre6','bin','client','jvm.dll'), "-Djava.class.path=%s" % os.path.join(os.getenv('TROBOT'), 'libs', 'soapui-4.5.1', 'lib', 'ojdbc5.jar'))
            pass

    def stop_jdbc(self):
        logger.debug(" ... in tdk_dbi.stop_jdbc ... ")
        #jpype.shutdownJVM()
		
