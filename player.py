# -*- coding:utf-8 -*-
import time
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from datetime import datetime, timedelta
from lxml.etree import HTML
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException, NoSuchWindowException

from page_obj import PageObject
from utils import load_json, cookies_variable, save_json

DISPLAY_BLOCK = 'display: block'
FINISH = object()
COURSE_TYPE = {'所有': 'all', '专业课程': 15, '行业公需': 16, '一般公需': 17}


class Player(object):
    def __init__(self):
        super().__init__()
        self.config = load_json('./config_define.json')
        self.type_num = COURSE_TYPE[self.config.get('course_type')]
        self.current_page = 1
        self.base_url = 'https://learning.hzrs.hangzhou.gov.cn/course/index.php?offset={}&ckeywords=%E8%AF%B7%E8%BE%93%E5%85%A5%E5%85%B3%E9%94%AE%E5%AD%97%E6%9F%A5%E8%AF%A2&examtype=W&coursetype={}&'
        cookies = self.load_cookies()
        self.browser = PageObject(self.base_url.format(self.current_page, self.type_num), cookies, self.config['headless'])

        self.course_urls = self.get_current_page_courses_link()

    def load_cookies(self):
        for cookie in cookies_variable:
            if cookie['name'] == 'learning':
                cookie['value'] = self.config['learning']
            if cookie['name'] == 'SESSID':
                cookie['value'] = self.config['SESSID']
        return cookies_variable

    def next_page(self):
        self.current_page = self.current_page + 1
        self.browser.get(self.base_url.format(self.current_page, self.type_num))

    def get_current_page_courses_link(self):
        links = self.browser.browser.find_elements_by_xpath('//div[@class="all-course"]/ul/li/a')
        urls = [link.get_attribute('href') for link in links]
        return urls

    def get_play_course_url(self):
        if len(self.course_urls) == 0:
            self.next_page()
            self.course_urls = self.get_current_page_courses_link()
            if len(self.course_urls) == 0:
                return None
        return self.course_urls.pop(0)

    def skip_time(self):
        from datetime import datetime, time as tt

        now = datetime.now().time()
        start_time = tt(9, 0)  # 设置开始时间为8点
        end_time = tt(21, 0)

        while now < start_time or now > end_time:
            print('waiting...')
            time.sleep(400)
            self.browser.browser.refresh()
            now = datetime.now().time()

    def play_course(self, link):
        print(f'course：{link}')
        self.config['current_course'] = link
        save_json(self.config, './config_define.json')
        self.browser.browser.set_page_load_timeout(6)
        try:
            self.browser.get(link)
        except TimeoutException:
            self.browser.execute_script("window.stop()")
        time.sleep(1)
        # self.skip_time()

        # click = self.browser.browser.find_element_by_xpath('//div[@class="c btnPos"]/button[1]')
        # click.click()
        self.browser.click('//div[@class="c btnPos"]/button[1]')
        self.browser.browser.switch_to_window(self.browser.window_handles[-1])
        self.current_time = "00:00:00"
        self.browser.browser.set_page_load_timeout(60)
        self.monitor_play_page()

    def switch_to_frame(self):
        self.browser.switch_to_frame('/html/frameset/frame')

    def play_page_1(self):
        if self.finish():
            return FINISH

        media = self.browser.locate_ele('//*[@id="media1_jwplayer_display_icon"]')
        if not media: return
        style = media.get_attribute('style')
        if style and DISPLAY_BLOCK in style:
            self.browser.click('//*[@id="mediaMaskBg"]')  # play
            self.browser.click('//*[@id="mediaMask"]')  # play

    def play_page_2(self):
        if self.finish():
            return FINISH

        media = self.browser.locate_ele('//div[@data-title="点击播放"]')
        if not media: return
        style = media.get_attribute('style')
        if style and DISPLAY_BLOCK in style:
            self.browser.click('//*[@id="timePanel"]')  # anchor
            self.browser.execute_script("arguments[0].click();", media)

    def play_page_3(self):
        self.browser.click('//*[@id="footer"]')  # anchor
        current_time = self.browser.execute_script('return document.getElementById("myVideo").currentTime;')
        total_time = self.browser.execute_script('return document.getElementById("myVideo").duration;')
        if current_time == total_time:
            return FINISH

        time.sleep(1)
        current_time_2 = self.browser.execute_script('return document.getElementById("myVideo").currentTime;')
        if current_time == current_time_2:
            self.browser.execute_script('document.getElementById("myVideo").play()')

    def play_page_4(self):
        if self.finish():
            return FINISH

        media = self.browser.locate_ele('//*[@id="toPlay"]')
        if not media: return
        style = media.get_attribute('style')
        if style and DISPLAY_BLOCK in style:
            media.click()
        elif not style:
            media.click()

    def play_page_5(self):
        try:
            if self.finish():
                return FINISH

            media = self.browser.locate_ele('//*[@id="media1_jwplayer_display_iconBackground"]')
            media_2 = self.browser.locate_ele('//*[@id="media1_jwplayer_display_text"]')
            if not (media or media_2): return
            style = media.get_attribute('style')
            style_2 = media_2.get_attribute('style')
            if (style and DISPLAY_BLOCK in style) or (style_2 and DISPLAY_BLOCK in style_2):
                self.browser.click('//*[@id="mediaMask"]')  # play
        except UnexpectedAlertPresentException:
            self.browser.switch_to_alert_accept()

    def get_current_play_page(self, retry=None):
        self.browser.locate_ele_long('//body')
        doc = HTML(self.browser.page_source)
        page_5 = doc.xpath('//*[@id="mediaMask"]')
        if page_5:
            print('play_page_5')
            return self.play_page_5
        page_1 = doc.xpath('//*[@id="media1_jwplayer_display_icon"]')  # 暂停的页面
        if page_1:
            print('play_page_1')
            return self.play_page_1
        page_2 = doc.xpath('//*[@id="timePanel"]')
        if page_2:
            print('play_page_2')
            return self.play_page_2
        page_3 = doc.xpath('//*[@id="myVideo"]')  # 调用js播放的页面
        if page_3:
            print('play_page_3')
            return self.play_page_3
        page_4 = doc.xpath('//*[@id="nextButton"]')
        # page_4 = doc.xpath('//*[@id="toPause"]')
        if page_4:
            print('play_page_4')
            return self.play_page_4
        if not retry:
            return self.get_current_play_page(retry=1)
        print("Can't locate the play page")

    def finish(self):
        current_time = self.browser.locate_ele('//*[@id="currentTimeLabel"]')
        total_time = self.browser.locate_ele('//*[@id="totalTimeLabel"]')
        if current_time and total_time:
            current_time = current_time.text
            if not current_time:
                doc = HTML(self.browser.page_source)
                current_time = ''.join(doc.xpath('//*[@id="currentTimeLabel"]/text()')).strip()
            if current_time >= total_time.text:
                return True
            if current_time and self.current_time:
                if datetime.strptime(current_time, '%H:%M:%S') + timedelta(minutes=2) < datetime.strptime(
                        self.current_time, '%H:%M:%S'):
                    return True
                self.current_time = current_time

    def monitor_play_page(self):
        open_frame = None
        current_page_func = None
        while True:
            time.sleep(3)
            try:
                if not open_frame:
                    self.switch_to_frame()
                    open_frame = True
                if not current_page_func:
                    current_page_func = self.get_current_play_page()
                if current_page_func() is FINISH:
                    break
            except AttributeError:
                self.browser.switch_to_alert_accept()
            except UnexpectedAlertPresentException:
                self.browser.switch_to_alert_accept()
            except NoSuchWindowException:
                break
            except TypeError as e:
                print(e)
                self.browser.switch_to_alert_accept()
            except TimeoutException as e:
                print(e)
                self.browser.switch_to_alert_accept()
        self.browser.browser.switch_to_window(self.browser.window_handles[0])

    def run(self):
        flag = False
        current_course_url = self.config.get('current_course')
        play_url = self.get_play_course_url()
        while play_url:
            if not current_course_url:
                self.play_course(play_url)
            elif current_course_url == play_url:
                self.play_course(play_url)
                flag = True
            elif flag:
                self.play_course(play_url)
            play_url = self.get_play_course_url()


if __name__ == '__main__':
    play = Player()
    play.run()
