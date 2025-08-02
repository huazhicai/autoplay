# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException, \
    NoSuchWindowException

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# chrome_options.add_argument("--user-data-dir=E:\\Projects\\autoplay\\automationprofile")

# 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出
# desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略页面加载策略
# desired_capabilities["pageLoadStrategy"] = "none"


class PageObject(object):
    """页面基本操作类"""

    def __init__(self, start_url, cookies, headless=None):
        chrome_options = Options()
        chrome_options.add_experimental_option(
            'excludeSwitches',
            ['enable-automation', 'ignore-certificate-errors', 'enable-logging'])
        prefs = {"credentials_enable_service": False, "profile.password_manager_enabled": False}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument('--start-maximized')
        if headless:
            chrome_options.add_argument('--headless')

        self.browser = webdriver.Chrome(options=chrome_options)
        self.long_wait = WebDriverWait(self.browser, 33)
        self.short_wait = WebDriverWait(self.browser, 9)
        self.load_cookies(start_url, cookies)

    def load_cookies(self, url, cookies_variable):
        self.browser.get(url)
        self.browser.delete_all_cookies()
        for cookie in cookies_variable:
            self.browser.add_cookie(cookie)
        self.browser.get(url)

    def get(self, url):
        self.browser.get(url)

    def switch_to_alert_accept(self):
        try:
            import time
            time.sleep(3)
            self.browser.switch_to.alert.accept()
            print('close alert')
        except NoAlertPresentException:
            print('no alert')
        except NoSuchWindowException:
            print('no such window')

    def switch_to_frame(self, xpath):
        try:
            frame = self.locate_ele(xpath)
            # if not frame:
            #     frame = self.browser.find_element_by_xpath(xpath)
            self.browser.switch_to.frame(frame)
            iframe = self.locate_ele('//iframe')
            # if not iframe:
            #     iframe = self.browser.find_element_by_xpath('//iframe')
            if iframe:
                self.browser.switch_to.frame(iframe)
        except TimeoutException as e:
            print(f'switch_to_frame timeout: {e}')

    @property
    def current_url(self):
        return self.browser.current_url

    @property
    def current_window_handle(self):
        return self.browser.current_window_handle

    @property
    def window_handles(self):
        return self.browser.window_handles

    @property
    def page_source(self):
        return self.browser.page_source

    def input(self, xpath, text):
        """输入框"""
        input_box = self.long_wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        input_box.clear()
        input_box.send_keys(text)

    def click(self, xpath):
        try:
            submit = self.long_wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            submit.click()
        except TimeoutException as e:
            print(e, xpath)
            return False
        except UnexpectedAlertPresentException as e:
            self.switch_to_alert_accept()

    def locate_ele_long(self, xpath):
        try:
            return self.long_wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException as e:
            print(f'Locate Failed {e}{xpath}')
        except UnexpectedAlertPresentException as e:
            self.switch_to_alert_accept()

    def locate_ele(self, xpath):
        try:
            return self.short_wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        except UnexpectedAlertPresentException as e:
            try:
                import time
                time.sleep(3)
                self.browser.switch_to.alert.accept()
                print('close alert')
            except NoAlertPresentException:
                print('no alert')
        except Exception as e:
            print(e)

    def execute_script(self, script, *args):
        return self.browser.execute_script(script, *args)

    def close(self):
        self.browser.close()
