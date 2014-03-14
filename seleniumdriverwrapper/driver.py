# -*- coding: utf-8 -*-
"""
Wrapper for seleniums webdriver
"""

import time
import datetime
from selenium import webdriver
from selenium.webdriver import Safari, Opera, Chrome, Firefox, PhantomJS
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, \
                                       WebDriverException, ElementNotVisibleException, \
                                       NoAlertPresentException, InvalidElementStateException


class Driver(object):
    """ Wrapper class for web-driver """

    __capabilities__ = {'safari': DesiredCapabilities.SAFARI,
                        'opera': DesiredCapabilities.OPERA,
                        'chrome': DesiredCapabilities.CHROME,
                        'firefox': DesiredCapabilities.FIREFOX,
                        'android': DesiredCapabilities.ANDROID,
                        'phatomjs': DesiredCapabilities.PHANTOMJS}

    __drivers__ = {'safari': Safari,
                   'opera': Opera,
                   'chrome': Chrome,
                   'firefox': Firefox,
                   'phantomjs': PhantomJS}

    def __init__(self, driver=None, timeout=5, poll=0.5, delay=0, screenshot_on_failure=False):
        if driver is not None and not isinstance(driver, WebDriver):
            raise TypeError("Given driver is not an instance of WebDriver")
        self.__driver = driver
        self.__current_elm = None
        self.timeout = timeout
        self.poll = poll
        self.delay = delay
        self.take_screenshot_on_failure = screenshot_on_failure
        self.screenshot_path = ''

    def __getattr__(self, attr):
        try:
            orig_attr = self.__driver.__getattribute__(attr)
        except AttributeError:
            orig_attr = self.__current_elm.__getattribute__(attr)

        if callable(orig_attr):
            def hooked(*args, **kwargs):
                """ Create and return a wrapper function """
                result = self._run(orig_attr, *args, **kwargs)
                if isinstance(result, WebElement):
                    self.__current_elm = result
                return self
            return hooked
        else:
            return orig_attr

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    def _run(self, fun, *args):
        """ Run function fun and take screenshot on failure """
        time.sleep(self.delay)
        try:
            return fun(*args)
        except Exception, ex:
            if self.take_screenshot_on_failure:
                self.take_screenshot()
            self.close()
            raise ex

    def _wait_until_displayed(self):
        """ Wait for an element to be displayed """
        try:
            WebDriverWait(self.__current_elm, self.timeout, self.poll).until(lambda d: d.is_displayed())
        except TimeoutException:
            raise ElementNotVisibleException('Waited for {0} seconds for element to be displayed but it never showed up'.format(self.timeout))

    def _find_elm(self, fun):
        """ Wait and search for en element """
        try:
            self.__current_elm = WebDriverWait(self.__driver, self.timeout, self.poll).until(fun)
            return self
        except TimeoutException:
            self.__current_elm = None
            raise NoSuchElementException('Waited for {0} seconds for element to be displayed but it never showed up'.format(self.timeout))

    def _alert(self):
        """ Helper function, Wait for an alert and return a selenium.webdriver.common.alert.Alert """
        timeout = self.timeout
        while timeout > 0:
            try:
                return self.__driver.switch_to_alert()
            except NoAlertPresentException:
                time.sleep(self.poll)
                timeout = timeout - self.poll
        raise NoAlertPresentException('Waited for for an alert to be displayed but it never came.'.format(self.timeout))

    def _click(self):
        """ Clicks the element """
        self._wait_until_displayed()
        pos_x = self.__current_elm.location['x']
        pos_y = self.__current_elm.location['y']
        self.scroll_to(pos_x, pos_y)
        return self.__current_elm.click()


    ###
    ### Public API
    ###

    def connect_remote(self, driver_name, command_executor, **kwargs):
        """ Connect to selenium """
        driver_name = driver_name.lower()
        if driver_name in self.__capabilities__:
            desired_capabilities = self.__capabilities__[driver_name]
            self.__driver = webdriver.Remote(command_executor, desired_capabilities, **kwargs)
        else:
            error = 'Unknown driver name. Should be one off {0}. {1} was given.\n'.format(', '.join('{}'.format(key) for key in self.__capabilities__.keys()), driver_name)
            raise NameError(error)

    def connect_local(self, driver_name, *args, **kwargs):
        """ Connect to a local browser """
        driver_name = driver_name.lower()
        if driver_name in self.__drivers__:
            self.__driver = self.__drivers__[driver_name](*args, **kwargs)
        else:
            error = 'Unknown driver name. Should be one off {0}. {1} was given.\n'.format(', '.join('{}'.format(key) for key in self.__drivers__.keys()), driver_name)
            raise NameError(error)

    def get_driver(self):
        """ Return wrapped driver """
        return self.__driver

    def get_current_element(self):
        """ Get current element """
        return self.__current_elm

    def dump_elm(self):
        """ Dumps information about current element """
        elm_list = self.__current_elm
        elm_info = 'Dump of current selected element:\n'
        if elm_list is not None:
            if not isinstance(elm_list, list):
                elm_list = [elm_list]
            for elm in elm_list:
                elm_info += '{0}\n'.format('\n'.join('{0}: {1}'.format(pro, elm.value_of_css_property(pro)) for pro in ['height', 'width', 'display', 'visibility']))
                elm_info += 'Position:\n\tx: {0}\n\ty: {1}\n'.format(elm.location['x'], elm.location['y'])
        else:
            elm_info += 'Element is of nonetype'
        print elm_info

    def take_screenshot(self, name=None, ext='png'):
        """ Takes a screenshot of the current window """
        name = name or datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        if not self.__driver.get_screenshot_as_file(self.screenshot_path + name + '.' + ext):
            print 'Unable to save screenshot'

    def get_alert(self):
        """ Wait for an alert and return a selenium.webdriver.common.alert.Alert """
        return self._run(self._alert)

    def scroll_to(self, pos_x, pos_y):
        """ Scrolls the window to a particular place in the document """
        self._run(self.__driver.execute_script, "window.scrollTo({0}, {1})".format(pos_x, pos_y))

    def attr(self, name):
        """ Gets the attribute value """
        if self.__current_elm is not None:
            return self._run(self.__current_elm.get_attribute, name)
        else:
            raise TypeError("No element is selected")

    def click(self):
        """ Clicks the element """
        if self.__current_elm is not None:
            return self._run(self._click)
        else:
            raise TypeError("No element is selected")

    def find_by_css(self, target, single=True):
        """ Find element by css """
        if single:
            return self._run(self._find_elm, lambda d: d.find_element_by_css_selector(target))
        else:
            return self._run(self._find_elm, lambda d: d.find_elements_by_css_selector(target))

    def find_by_xpath(self, target, single=True):
        """ Find element by xpath """
        if single:
            return self._run(self._find_elm, lambda d: d.find_element_by_xpath(target))
        else:
            return self._run(self._find_elm, lambda d: d.find_elements_by_xpath(target))

    def find_by_name(self, name, single=True):
        """ Find element by name """
        if single:
            return self._run(self._find_elm, lambda d: d.find_element_by_name(name))
        else:
            return self._run(self._find_elm, lambda d: d.find_element_by_name(name))

    def find_link_by_text(self, text, single=True, silent=False):
        """ Find element by link text """
        if single:
            if silent:
                try:
                    self._find_elm(lambda d: d.find_element_by_link_text(text))
                except NoSuchElementException:
                    pass
                return self
            else:
                return self._run(self._find_elm, lambda d: d.find_element_by_link_text(text))
        else:
            return self._run(self._find_elm, lambda d: d.find_elements_by_link_text(text))

    def find_by_text(self, text, tag="*", partial=False, single=True):
        """ Find element by text """
        if partial:
            return self.find_by_xpath(".//%s[contains(text(), '%s')]" % (tag, text), single)
        return self.find_by_xpath(".//%s[text()='%s']" % (tag, text), single)

    def find_href(self, url=None, single=False):
        """ Find an element that links to `url` """
        return self.find_by_xpath(".//a[contains(@href, '%s')]" % (url), single)

    def find_button(self, value, single=True):
        """ Find button """
        return self.find_by_xpath(".//input[(@type='submit' or @type='button') and @value='%s']" % value, single)

    def press_enter(self):
        """ Press the enter key """
        if self.__current_elm is not None:
            self.__current_elm.send_keys(Keys.RETURN)
        else:
            raise TypeError("No element is selected")

    def switch_to_frame(self, id_name=None, class_name=None, name=None):
        """ Switch to frame """
        if id_name is not None:
            self._find_elm(lambda d: d.find_element_by_id(id_name))
        elif class_name is not None:
            self._find_elm(lambda d: d.find_element_by_class(class_name))
        elif name is not None:
            self._find_elm(lambda d: d.find_element_by_name(name))
        else:
            self._find_elm(lambda d: d.find_element_by_tag_name("iframe"))

        self.__driver.switch_to_frame(self.__current_elm)

    def see(self, text):
        """ Find text on the page """
        self.find_by_text(text, partial=True)

    def do_not_see(self, text):
        """ Ensure that the text is not on the page """
        try:
            self._find_elm(lambda d: d.find_element_by_xpath(".//*[contains(text(), '%s')]" % (text)))
        except NoSuchElementException:
            # The element was not found
            return self
        else:
            print self.dump_elm()
            raise InvalidElementStateException('Text was found')

    def find_by_jquery(self, jquery_selector, iframe_selector=None):
        """ Find element with help of jquery """
        if iframe_selector is None:
            javascript = "return $('{0}')[0]".format(jquery_selector)
        else:
            javascript = "return $('{0}').contents().find('{1}')[0]".format(iframe_selector, jquery_selector)

        try:
            result = self.__driver.execute_script(javascript)
        except WebDriverException, wde:
            print "\033[91m" + "Make sure that jQuery is loaded" + "\033[0m"
            raise wde

        if result:
            self.__current_elm = result
        else:
            self.__current_elm = None
        return self

    def sleep(self, sec):
        """ Explicit wait """
        time.sleep(sec)

    @property
    def am_on(self):
        """ Get the current url """
        return self.__driver.current_url

    def die(self):
        """ Closes the current window """
        self.__driver.close()
