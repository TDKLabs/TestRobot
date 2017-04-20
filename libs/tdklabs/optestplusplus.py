#
# Common OpTest++ functions and global / shared common variables should be placed here ...
#


import tdk
import tdk_dbi
import unittest
import pytest
import time
import datetime
import os
import sys
import sst.actions

from robot.api import logger

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains


######################################################
# All test scripts should subclass WebBaseTest.
######################################################

__TESTCASE_ID__ = None

class WebBaseTest(unittest.TestCase):

	dbi = None
	
	@classmethod
	def setUpClass(cls):
		# start selenium session browser as part of test module initialization
		for i in range(0,5):
			try:
				start()				
			except WebDriverException as e: 
				sst.actions._print("!!!! WARN Caught WebDriverException after start(): " + str(i) + " - " + str(e) + " !!!!")
				if i==3: 
					if sys.platform == "win32":
						if tdk.BROWSER == "Firefox":
							os.system("taskkill /F /IM firefox.exe")						
					else:
						os.system("killall firefox")
				if i==4: raise e
				sleep((i+1)*15)
			else:
				sst.actions._print("=> No exceptions after start() <=")
				break	
		
	@classmethod
	def tearDownClass(cls):
		# shutdown selenium browser
		stop()
		
	def setUp(self):
		# any commands needed as part of test case initialization
		global __TESTCASE_ID__
		__TESTCASE_ID__ = self.id()
		
	def tearDown(self):
		# any commands needed as part of test case tear down
		pass

######################################################		


trobot_logger = sst.actions._print


###################################################### 
# Decorator / listener for hooking into assertion 
# failures
###################################################### 
class FailedSeleniumAssertion(object):
	def __init__(self, error, screenshot, pagedump):
		self.error = error
		self.screenshot = screenshot
		self.pagedump = pagedump
		
	def __call__(self, f):
		def wrappedfunction(*args, **kwargs):
			try:
				return f(*args, **kwargs)
			except self.error as err:	
				sst.actions._print("Caught an Error: <<< " + str(err) + " ::: " + str(sys.exc_info()[1]) + " >>>")
				if self.screenshot is not None: self.screenshot()
				if self.pagedump is not None: self.pagedump() 
				raise
		return wrappedfunction	
###################################################### 


###################################################### 
# initialization 
###################################################### 
sst.config.results_directory = os.getenv('SCREENSHOT_DIR','screenshots')
tdk.SCREENSHOT_DIR = sst.config.results_directory
sst.actions._make_results_dir()

mark = pytest.mark

_display = None
def setUpModule():
	if sys.platform.startswith("linux"):
		from pyvirtualdisplay import Display
		_display = Display(visible=0, size=(1280,1024))
	else:
		_display = None
		
	# start up jdbc
	
	
def tearDownModule():
	if _display != None:
		_display.stop()
	
	# shutdown jdbc
	


def SetUpSuite():
	start()

def TearDownSuite():
	stop()

###################################################### 	
	
	
######################################################     
# browser management functions    
######################################################
def take_screenshot(name=None):
	global __TESTCASE_ID__
	
	if name==None:
		filename = '%s.png' % __TESTCASE_ID__
	else:
		filename = '%s.png' % (str(name)+'-'+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	sst.actions.take_screenshot(filename)
	with open(os.path.join(tdk.SCREENSHOT_DIR,filename),'rb') as f:
		import base64
		logger.info('<img src="data:image/png;base64,%s" width="1200px"/>' % (base64.b64encode(f.read())), True, False)
    
def dump_pagesource(name=None):
	global __TESTCASE_ID__
	
	sst.actions._print('Capturing page source')
	if name==None:
		filename = '%s.html' % __TESTCASE_ID__
	else:
		filename = '%s.html' % name

	path = os.path.join(sst.config.results_directory, filename)
	import codecs
	with codecs.open(path, 'w', encoding='utf-8') as f:
		f.write(sst.actions.get_page_source())

def start():
    sst.actions.start()
    
def stop():
    sst.actions.stop()
    
def go_to(url):
    sst.actions.go_to(url)    
    sst.actions.sleep(0.5)

def go_back():
    sst.actions.go_back()
    
def set_base_url(url):
	sst.actions.set_base_url(url)

def get_base_url(url):
	return sst.actions.get_base_url(url)

def get_current_url():
    return sst.actions.get_current_url()
	
def get_page_source():
    return sst.actions.get_page_source()

def sleep(secs):
    sst.actions.sleep(secs)

def refresh():
    sst.actions.refresh()

def maximize_window():
	get_selenium_driver_object().maximize_window()	

def close_window():
	sst.actions.close_window()
	
def clear_cookies():
	sst.actions.clear_cookies()
	
def get_cookies():
	return sst.actions.get_cookies()

def get_element_source(id_or_elem):
	return sst.actions.get_element_source(id_or_elem)

@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException), screenshot=take_screenshot, pagedump=dump_pagesource)	
def get_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs):
	for i in xrange(30):
		try:
			elem = sst.actions.get_element(tag=tag, css_class=css_class, id=id, text=text, text_regex=text_regex, **kwargs)
			return elem
		except StaleElementReferenceException:
			sst.actions._print(" !!! @@@ Trying to recover from StaleElementReferenceException. Attempt #(%s/%s) @@@ !!! " % (i,29))
			if i==29:
				sst.actions._print(" !!! Giving up. It's not there !!! ")
				raise
			sst.actions.sleep(1)

@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException), screenshot=take_screenshot, pagedump=dump_pagesource)
def get_elements(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs):
	for i in xrange(30):
		try:
			elems = sst.actions.get_elements(tag=tag, css_class=css_class, id=id, text=text, text_regex=text_regex, **kwargs)
			return elems
		except StaleElementReferenceException:
			sst.actions._print(" !!! @@@ Trying to recover from StaleElementReferenceException. Attempt #(%s/%s) @@@ !!! "     % (i,29))
			if i==29:
				sst.actions._print(" !!! Giving up. It's not there !!! ")
				raise
			sst.actions.sleep(1)

@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException), screenshot=take_screenshot, pagedump=dump_pagesource)
def get_elements_by_css(selector):
	for i in xrange(30):
		try:
			elems = sst.actions.get_elements_by_css(selector)
			return elems
		except StaleElementReferenceException:
			sst.actions._print(" !!! @@@ Trying to recover from StaleElementReferenceException. Attempt #(%s/%s) @@@ !!! " % (i,29))
			if i==29:
				sst.actions._print(" !!! Giving up. It's not there !!! ")
				raise
			sst.actions.sleep(1)
	
@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException), screenshot=take_screenshot, pagedump=dump_pagesource)
def get_element_by_css(selector):	
	for i in xrange(30):
		try:
			elem = sst.actions.get_element_by_css(selector)
			return elem
		except StaleElementReferenceException:
			sst.actions._print(" !!! @@@ Trying to recover from StaleElementReferenceException. Attempt #(%s/%s) @@@ !!! " % (i,29))
			if i==29:
				sst.actions._print(" !!! Giving up. It's not there !!! ")
				raise
			sst.actions.sleep(1)

@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException), screenshot=take_screenshot, pagedump=dump_pagesource)
def get_element_by_xpath(selector):
	for i in xrange(30):
		try:
			elem = sst.actions.get_element_by_xpath(selector)
			return elem
		except StaleElementReferenceException:
			sst.actions._print(" !!! @@@ Trying to recover from StaleElementReferenceException. Attempt #(%s/%s) @@@ !!! " % (i,29))
			if i==29:
				sst.actions._print(" !!! Giving up. It's not there !!! ")
				raise
			sst.actions.sleep(1)

@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException), screenshot=take_screenshot, pagedump=dump_pagesource)
def get_elements_by_xpath(selector):
	for i in xrange(30):
		try:
			elems = sst.actions.get_elements_by_xpath(selector)
			return elems
		except StaleElementReferenceException:
			sst.actions._print(" !!! @@@ Trying to recover from StaleElementReferenceException. Attempt #(%s/%s) @@@ !!! " % (i,29))
			if i==29:
				sst.actions._print(" !!! Giving up. It's not there !!! ")
				raise
			sst.actions.sleep(1)


@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def exists_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs):
    if kwargs.has_key("xpath"):
        selector = kwargs.get("xpath")
        try:
            sst.actions.get_elements_by_xpath(selector)
            return True
        except AssertionError:
            return False
    else:
        try:
            ret = sst.actions.exists_element(tag=tag, css_class=css_class, id=id, text=text, text_regex=text_regex, **kwargs)
            return ret
        except:
            return False


def _elem_is_not_stale(elem):
	try:
		# Calling any method forces a staleness check
		elem.is_enabled()
		return True
	except StaleElementReferenceException:
		return False

def _elem_with_id_is_not_stale(id):
	try:
		get_selenium_driver_object().find_element_by_id(id).is_enabled()
		return True
	except StaleElementReferenceException: 
		return False
	except (NoSuchElementException, WebDriverException):
		sst.actions._raise('Element with id: %r does not exist' % id)

@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException,TimeoutException), screenshot=take_screenshot, pagedump=dump_pagesource)	
def click_link(id_or_elem):
	if isinstance(id_or_elem, WebElement):
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")
	else:
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_with_id_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")

	sst.actions.click_link(id_or_elem)	


@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException,TimeoutException), screenshot=take_screenshot, pagedump=dump_pagesource)	
def click_element(id_or_elem):
	if isinstance(id_or_elem,WebElement):
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")
	else:
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_with_id_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")

	sst.actions.click_element(id_or_elem)	


@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException,TimeoutException), screenshot=take_screenshot, pagedump=dump_pagesource)	
def click_button(id_or_elem):
	if isinstance(id_or_elem,WebElement):
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")
	else:
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_with_id_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")

	sst.actions.click_button(id_or_elem)	


@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def write_textfield(id_or_elem, text, use_keys=False, check=True, clear=True):
        if use_keys:
                sst.actions.write_textfield(id_or_elem, text, check, clear)
        else:
		elem = sst.actions.assert_textfield(id_or_elem)
		text = text.replace("'",'"')
		text = text.replace("\r\n","")
		text = text.replace("\n","")
		sst.actions.execute_script("arguments[0].value='%s';"%text, elem)


@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException,TimeoutException), screenshot=take_screenshot, pagedump=dump_pagesource)
def toggle_checkbox(id_or_elem):
	if isinstance(id_or_elem,WebElement):
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")
	else:
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_with_id_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")

	sst.actions.toggle_checkbox(id_or_elem)	


def set_wait_timeout(timeout):
	sst.actions.set_wait_timeout(timeout)
	
def nwait_for(*args, **kwargs):
	"""
	This is a enhanced wait for function (new wait for) 
	wait for function sometimes throwing an exception when handling popups 
	this new function handles the exception and waits for some element or action
	_maxwaiting time variable defines maximum waiting time
	"""
	_maxwaitingtime=12 
	_flag=0
	_future = time.time() + _maxwaitingtime
	while time.time() < _future:
		try:
			sst.actions.wait_for(*args,**kwargs)
		except:
			sleep(0.3)
			sst.actions._print(" ... waiting in nwait_for ... ")
		else:
			_flag=1
			break
	
	if _flag==0:
		assert_fail("Failed in (nwait_for)!")
	else:
		sst.actions._print("New Wait for success")	
	
def wait_for(condition, *args, **kwargs):
	sst.actions.wait_for(condition, *args, **kwargs)
	
def wait_for_and_refresh(condition):
	sst.actions.wait_for_and_refresh(condition)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, NoSuchAttributeException,
    InvalidElementStateException, WebDriverException,
    NoSuchWindowException, NoSuchFrameException, ElementNotVisibleException, TimeoutException, StaleElementReferenceException)
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def wait_for_element_visible(searchType, locator, explicitWait):
	"""
	This function support the dynamic asynchronous wait mechanism available for the handler to 'explicitly" wait for an element against UI.
	Satisfy the requirement to check if an element is present on the DOM of a page and visible. Confirmed that the element is not only displayed
	but also has a height and width that is greater than 0 (thus eliminating rendering/ajax issues)
	"""
	if searchType == "id":
		by = By.ID
	elif searchType == "xpath":
		by = By.XPATH
	elif searchType == "link_text":
		by=By.LINK_TEXT
	elif searchType == "partial_link_text":
		by = By.PARTIAL_LINK_TEXT
	elif searchType == "name":
		by = By.NAME
	elif searchType == "tag_name":
		by = By.TAG_NAME
	elif searchType == "class_name":
		by = By.CLASS_NAME
	elif searchType == "css":
		by = By.CSS_SELECTOR
	else:
		#Default case
		by = By.ID

	try:
		elem = WebDriverWait(get_selenium_driver_object(), explicitWait).until(EC.visibility_of_element_located((by, locator)))
	except(ElementNotVisibleException, TimeoutException):
		sst.actions._raise('Element with locator: (%s) is not visible' % locator)
	except(StaleElementReferenceException):
		sst.actions._raise('Selenium Stale exception has occurred. Looks like the element you are looking out for is no longer available in the DOM.')


@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException,TimeoutException), screenshot=take_screenshot, pagedump=dump_pagesource)
def set_dropdown_value(id_or_elem, text=None, value=None):
	if isinstance(id_or_elem,WebElement):
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")
	else:
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_with_id_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")

	sst.actions.set_dropdown_value(id_or_elem, text, value)		


@FailedSeleniumAssertion(error=(AssertionError,StaleElementReferenceException,TimeoutException), screenshot=take_screenshot, pagedump=dump_pagesource)
def set_radio_value(id_or_elem):
	if isinstance(id_or_elem,WebElement):
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")
	else:
		WebDriverWait(get_selenium_driver_object(),timeout=30,ignored_exceptions=StaleElementReferenceException).until(lambda _: _elem_with_id_is_not_stale(id_or_elem)," !!! Giving up. It's not there !!! ")

	sst.actions.set_radio_value(id_or_elem)	

	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def set_checkbox_value(id_or_elem, new_value):
    sst.actions.set_checkbox_value(id_or_elem, new_value)
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def get_text(elem):
	sst.actions._get_text(elem)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def simulate_keys(id_or_elem, key_to_press):
	sst.actions.simulate_keys(id_or_elem, key_to_press)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def accept_alert(expected_text=None, text_to_write=None):
    sst.actions.accept_alert(expected_text, text_to_write)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def dismiss_alert(expected_text=None, text_to_write=None):
    sst.actions.dismiss_alert(expected_text, text_to_write)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def switch_to_frame(index_or_name=None):
    sst.actions.switch_to_frame(index_or_name)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def switch_to_window(index_or_name=None):
    sst.actions.switch_to_window(index_or_name)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def execute_script(script, *args):
    return sst.actions.execute_script(script, *args)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def scroll(x=0, y=0):
    return sst.actions.execute_script("window.scrollTo({}, {});".format(x, y))

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def scroll_bottom():
    return sst.actions.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def get_selenium_driver_object():
	"""Get the underlying selenium webdriver object instance"""
	return sst.actions.browser
	
###################################################### 
	
	
######################################################
# assertion functions    
######################################################
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_fail(msg):
    assert False, msg

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_dropdown(id_or_elem):
	sst.actions.assert_dropdown(id_or_elem)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_dropdown_value(id_or_elem, text_in):
	sst.actions.assert_dropdown_value(id_or_elem, text_in)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_radio(id_or_elem):
	sst.actions.assert_radio(id_or_elem)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_radio_value(id_or_elem, value):
	sst.actions.assert_radio_value(id_or_elem, value)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs):
	sst.actions.assert_element(tag=tag, css_class=css_class, id=id, text=text, text_regex=text_regex, **kwargs)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_button(id_or_elem):
	sst.actions.assert_button(id_or_elem)
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_textfield(id_or_elem):
	assert sst.actions.assert_textfield(id_or_elem) is not None

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_checkbox(id_or_elem):
	assert sst.actions.assert_checkbox(id_or_elem) is not None
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_link(id_or_elem):
	assert sst.actions.assert_link(id_or_elem) is not None

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_element_exist(id):
	assert sst.actions.exists_element(id=id), "Element %s doesn't exist" % id

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_element_not_exist(id):
	assert not sst.actions.exists_element(id=id), "Element %s does exist" % id

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs):
	assert sst.actions.assert_element(tag=tag, css_class=css_class, id=id, text=text, text_regex=text_regex, **kwargs) is not None
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_attribute(id_or_elem, attribute, value, regex=True):
	sst.actions.assert_attribute(id_or_elem, attribute, value, regex)
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_css_property(id_or_elem, property, value, regex=True):
	sst.actions.assert_css_property(id_or_elem, property, value, regex)	
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_displayed(id_or_elem):
	assert sst.actions.assert_displayed(id_or_elem) is not None
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_not_displayed(id_or_elem):
	assert sst.actions.assert_displayed(id_or_elem) is None

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_page_contains(text):
	_assert_in_page(text)
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_page_does_not_contain(text):
	_assert_not_in_page(text)
			
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)				
def assert_title(title):
	sst.actions.assert_title(title)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)		
def assert_title_contains(text, regex=True):
	sst.actions.assert_title_contains(text, regex)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)		
def assert_url(url):
	sst.actions.assert_url(url)
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)		
def assert_url_contains(text, regex=True):
	sst.actions.assert_url_contains(text, regex)
    
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)		
def assert_table_has_rows(id_or_elem, num_rows):
	sst.actions.assert_table_has_rows(id_or_elem, num_rows)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_table_row_contains_text(id_or_elem, row, contents, regex=True):
	sst.actions.assert_table_row_contains_text(id_or_elem, row, contents, regex)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def  assert_table_headers(id_or_elem, headers):
    sst.actions.assert_table_headers(id_or_elem, headers)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_text(id_or_elem, text):
	sst.actions.assert_text(id_or_elem, text)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_text_contains(id_or_elem, text, regex=True):
	sst.actions.assert_text_contains(id_or_elem, text, regex)

def _assert_in_page(item, msg = "assertion failed: expected %(item)r in %(sequence)r"):
    """Assert that the item is in the sequence."""
    sequence = sst.actions.get_page_source()
    assert item in sequence, msg % {'item':item, 'sequence':sequence}

def _assert_not_in_page(item, msg="assertion failed: expected %(item)r not in %(sequence)r"):
    """Assert that the item is not in the sequence."""
    sequence = sst.actions.get_page_source()
    assert item not in sequence, msg % {'item':item, 'sequence':sequence}

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)
def assert_checkbox_value(id_or_elem, value):
    return sst.actions.assert_checkbox_value(id_or_elem, value)

@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_equal(first, second):
    """Assert two objects are equal."""
    sst.actions.assert_equal(first, second)
	
assert_equals = assert_equal	
	
@FailedSeleniumAssertion(error=AssertionError, screenshot=take_screenshot, pagedump=dump_pagesource)	
def assert_not_equal(first, second):
    """Assert two objects are not equal."""
    sst.actions.assert_not_equal(first, second)
	
assert_not_equals = assert_not_equal	
	


def trobot_check_point(mesg):
    logger.info(mesg, True, False)
    mesg = mesg.replace(" ", "_")
    take_screenshot(mesg)


def show(element, duration=5):
    """Highlights the specified element."""
    assert element != None
    style = element.get_attribute("style")
    sst.actions.execute_script("arguments[0].setAttribute('style',arguments[1]);",element,"border: 3px solid red; border-style: dashed;")
    if duration>0:
        sst.actions.sleep(duration)
        sst.actions.execute_script("arguments[0].setAttribute('style',arguments[1]);",element,style)


def mouse_over(element):
    js_mouse_over = "if(document.createEvent){var e = document.createEvent('MouseEvents'); e.initEvent('mouseover',true, false); arguments[0].dispatchEvent(e);} else if(document.createEventObject){arguments[0].fireEvent('onmouseover');}"
    sst.actions.execute_script(js_mouse_over, element)


def mouse_out(element): 
    js_mouse_out = "if(document.createEvent){var e = document.createEvent('MouseEvents'); e.initEvent('mouseout',true, false); arguments[0].dispatchEvent(e);} else if(document.createEventObject){arguments[0].fireEvent('onmouseout');}"
    sst.actions.execute_script(js_mouse_out, element)

def move_to_element(element):
    ActionChains(get_selenium_driver_object()).move_to_element(element).perform()        

def scroll_to_element(element):
    sst.actions.execute_script("arguments[0].scrollIntoView();", element)



