#
# Common OpTest library functions should be placed here ...
#

import sys
from robot.api import logger


logger.debug(" ... Importing optest library ... ")

class optest:

	def __init__(self, display_size=(1600,1200)):
		logger.debug(" ... in optest constructor ... ")
		if sys.platform.startswith("linux"):
			from pyvirtualdisplay import Display
			self.display = Display(visible=0, size=display_size)
		else:
			self.display = None

			
	def start_display(self):
		logger.debug(" ... in optest.start_display ... ")
		if self.display != None:
			self.display.start()
			if self.display.display:
				logger.info(" !!! WARN: display # (%d) !!! " % self.display.display, html=True, also_console=True)


	def stop_display(self):
		logger.debug(" ... in optest.stop_display ... ")
		if self.display != None:
			self.display.stop()
