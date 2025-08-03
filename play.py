# -*- coding:utf-8 -*-
import time

from playwright.sync_api import sync_playwright
import re
import json
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright

COURSE_TYPE = {'所有': 'all', '专业课程': 15, '行业公需': 16, '一般公需': 17}


class Course(object):
    def __init__(self, course_id, course_name):
        self.id = None
        self.name = None

    def play(self, page):
        url = f"https://learning.hzrs.hangzhou.gov.cn/#/class?courseId={self.id}&coursetitle={self.name}"

        print(url)
        page.goto(url)

        page.on("dialog", lambda dialog: dialog.accept())
        # 是否继续学习
        try:
            page.get_by_role("button", name="确定").click(timeout=2000)
        except Exception as e:
            pass

        try:  # 播放
            page.get_by_role("button", name="Play Video").click()
        except TimeoutError:
            pass

        # page.wait_for_selector(".vjs-duration-display")
        # duration = page.locator(".vjs-duration-display").inner_text()

        # 设定总播放时长（比如60分钟）
        total_watch_time_ms = 30 * 60 * 1000
        check_interval_ms = 3000
        elapsed = 0

        play_bar_button = page.locator('button.vjs-play-control')
        while elapsed < total_watch_time_ms:
            try:
                # 3️⃣ 如果出现“确定”按钮的 HTML 弹窗，点击它
                dialog_button = page.get_by_role("button", name="确定").wait_for(state="visible", timeout=3000)
                dialog_button.click(force=True)
                print("✅ 已点击弹窗‘确定’按钮")
            except Exception as e:
                pass
                print(f"🕐 [{time.strftime('%H:%M:%S')}] 无弹窗，继续播放:{str(e)}")

            try:
                # 监控是否播发完了
                title = play_bar_button.get_attribute("title")
                # print("当前title为：", title)

                if title == "Play":
                    play_bar_button.click()
                    print("点击播放")
                elif title == "Replay":
                    print("播放结束，关闭页面")
                    break
            except Exception as e:
                print(f"🕐 [{time.strftime('%H:%M:%S')}] title 失败:{str(e)}")
            # 每3秒检查一次
            page.wait_for_timeout(check_interval_ms)
            elapsed += check_interval_ms

        page.close()


class Page(object):
    def __init__(self):
        self.headless = False
        self.course_type = None
        self.current_page_num = None
        self.last_page = 10
        self.page_courses = []

        self.conf = {}
        self.conf_file = './config_define.json'
        self.base_url = 'https://learning.hzrs.hangzhou.gov.cn/#/'
        self.course_url = f"{self.base_url}class?courseId={self.current_course_id}&coursetitle={self.current_course_name}"

        self.load_config()

    def load_config(self):
        with open(self.conf_file, 'r', encoding="utf8") as f:
            self.conf = json.load(f)

        self.headless = self.conf.get('headless', False)
        self.course_type = self.conf.get('course_type')
        self.current_course_id = self.conf.get('current_course_id')
        self.current_course_name = self.conf.get('current_course_name')
        self.current_page = self.conf.get('current_page', 1)

    def save_config(self):
        self.conf['current_course_id'] = self.current_course_id
        self.conf['current_course_name'] = self.current_course_name
        self.conf['current_page'] = self.current_page

        with open(self.conf_file, 'w', encoding="utf8") as f:
            json.dump(self.conf, f)

    def get_last_page(self, page):
        selector = 'ul > li.number'
        all_last_page = page.locator(selector).last.text_content()
        while True:
            type_last_page = page.locator(selector).last.text_content()
            if type_last_page < all_last_page:
                break
            page.wait_for_timeout(1000)
        print(type_last_page)
        return type_last_page

    def on_response(self, response):
        """获取当前页面的课程"""
        if response.status == 200 and 'SelectCourse' in response.url:
            print(response.url)
            print(response.json())
            for item in response.json()['course']['data']:
                self.page_courses.append(Course(item['courseid'], item['coursename']))

    def play_course(self, page):
        course_url = f"{self.base_url}class?courseId={self.current_course_id}&coursetitle={self.current_course_name}"
        print(course_url)
        page.goto(course_url)

        page.on("dialog", lambda dialog: dialog.accept())
        # 是否继续学习
        try:
            page.get_by_role("button", name="确定").click(timeout=2000)
        except Exception as e:
            pass

        try:  # 播放
            page.get_by_role("button", name="Play Video").click()
        except TimeoutError:
            pass

        # page.wait_for_selector(".vjs-duration-display")
        # duration = page.locator(".vjs-duration-display").inner_text()

        # 设定总播放时长（比如60分钟）
        total_watch_time_ms = 30 * 60 * 1000
        check_interval_ms = 3000
        elapsed = 0

        play_bar_button = page.locator('button.vjs-play-control')
        while elapsed < total_watch_time_ms:
            try:
                # 3️⃣ 如果出现“确定”按钮的 HTML 弹窗，点击它
                dialog_button = page.get_by_role("button", name="确定").wait_for(state="visible", timeout=3000)
                dialog_button.click(force=True)
                print("✅ 已点击弹窗‘确定’按钮")
            except Exception as e:
                pass
                print(f"🕐 [{time.strftime('%H:%M:%S')}] 无弹窗，继续播放:{str(e)}")

            try:
                # 监控是否播发完了
                title = play_bar_button.get_attribute("title")
                # print("当前title为：", title)

                if title == "Play":
                    play_bar_button.click()
                    print("点击播放")
                elif title == "Replay":
                    print("播放结束，关闭页面")
                    break
            except Exception as e:
                print(f"🕐 [{time.strftime('%H:%M:%S')}] title 失败:{str(e)}")
            # 每3秒检查一次
            page.wait_for_timeout(check_interval_ms)
            elapsed += check_interval_ms

        page.close()

    def next_page(self, page):
        while True:
            try:
                page.get_by_role("listitem", name=f"第 {self.current_page + 1} 页").click(timeout=2000)
                page.wait_for_timeout(2000)
                self.current_page += 1
                break
            except Exception as e:
                page.get_by_role("listitem", name="向后 5 页").click()

    def get_current_page_courses(self, page):
        pass

    def play_current_page_courses(self, context):
        while len(self.page_courses) > 0:
            course = self.page_courses.pop()
            page = context.new_page()
            course.play(page)

    def run(self):
        with sync_playwright() as p:
            browser = p.webkit.launch(args=["--start-maximized"], headless=False, slow_mo=500)
            context = browser.new_context(storage_state="auth.json",
                                          viewport={"width": 1920, "height": 1080})  # 加载已保存的状态

            page = context.new_page()
            page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")  # 已是登录态

            page.get_by_role("button", name="学员登录").click()
            page.get_by_text("在线学习系统").click()

            page.get_by_text("网络课程").first.click()

            page.click("div.el-select__placeholder:has-text('--所有--')")
            page.click("li:has-text('行业公需')")

            last_page = self.get_last_page(page)
            page.on('response', self.on_response)

            current_page = 1
            while current_page <= 8:
                try:
                    self.play_current_page_courses(context)
                    page.get_by_role("listitem", name=f"第 {current_page} 页").click(timeout=1000)
                    current_page += 1
                    page.wait_for_timeout(1000)
                except Exception as e:
                    page.get_by_role("listitem", name="向后 5 页").click()

            page.wait_for_load_state('networkidle')

            input('anything....')
            browser.close()


if __name__ == '__main__':
    player = Page()
    player.run()
