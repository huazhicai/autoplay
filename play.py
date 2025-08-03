# -*- coding:utf-8 -*-
import time

from playwright.sync_api import sync_playwright
import re
import json
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright

COURSE_TYPE = {'所有': 'all', '专业课程': 15, '行业公需': 16, '一般公需': 17}


class Course:
    def __init__(self, course_id: str, course_name: str):
        self.id = course_id
        self.name = course_name

    def play(self, page):
        url = f"https://learning.hzrs.hangzhou.gov.cn/#/class?courseId={self.id}&coursetitle={self.name}"

        print(url)
        # page.goto(url)
        #
        # page.on("dialog", lambda dialog: dialog.accept())
        # # 是否继续学习
        # try:
        #     page.get_by_role("button", name="确定").click(timeout=2000)
        # except Exception as e:
        #     pass
        #
        # try:  # 播放
        #     page.get_by_role("button", name="Play Video").click()
        # except TimeoutError:
        #     pass
        #
        # # page.wait_for_selector(".vjs-duration-display")
        # # duration = page.locator(".vjs-duration-display").inner_text()
        #
        # # 设定总播放时长（比如60分钟）
        # total_watch_time_ms = 30 * 60 * 1000
        # check_interval_ms = 3000
        # elapsed = 0
        #
        # play_bar_button = page.locator('button.vjs-play-control')
        # while elapsed < total_watch_time_ms:
        #     try:
        #         # 3️⃣ 如果出现“确定”按钮的 HTML 弹窗，点击它
        #         dialog_button = page.get_by_role("button", name="确定").wait_for(state="visible", timeout=3000)
        #         dialog_button.click(force=True)
        #         print("✅ 已点击弹窗‘确定’按钮")
        #     except Exception as e:
        #         pass
        #         print(f"🕐 [{time.strftime('%H:%M:%S')}] 无弹窗，继续播放:{str(e)}")
        #
        #     try:
        #         # 监控是否播发完了
        #         title = play_bar_button.get_attribute("title")
        #         # print("当前title为：", title)
        #
        #         if title == "Play":
        #             play_bar_button.click()
        #             print("点击播放")
        #         elif title == "Replay":
        #             print("播放结束，关闭页面")
        #             break
        #     except Exception as e:
        #         print(f"🕐 [{time.strftime('%H:%M:%S')}] title 失败:{str(e)}")
        #     # 每3秒检查一次
        #     page.wait_for_timeout(check_interval_ms)
        #     elapsed += check_interval_ms
        #
        # page.close()


class Player(object):
    def __init__(self):
        self.headless = False
        self.course_type = None
        self.current_page_num = 1
        self.last_page_num = 10
        self.page_courses = []
        self.is_start_page = True

        self.conf = {}
        self.conf_file = './config_define.json'
        self.base_url = 'https://learning.hzrs.hangzhou.gov.cn/#/'
        self.course_url = f"{self.base_url}class?courseId={self.current_course_id}&coursetitle={self.current_course_name}"

        self.load_config()

    def load_config(self):
        with open(self.conf_file, 'r', encoding="utf8") as f:
            self.conf = json.load(f)

        self.headless = self.conf.get('headless', False)
        self.current_page_num = self.conf.get('current_page', 1)

        self.course_type = COURSE_TYPE[self.conf['course_type']]
        self.current_course_id = self.conf.get('current_course_id')
        self.current_course_name = self.conf.get('current_course_name')

    def save_config(self):
        self.conf['current_course_id'] = self.current_course_id
        self.conf['current_course_name'] = self.current_course_name
        self.conf['current_page'] = self.current_page_num

        with open(self.conf_file, 'w', encoding="utf8") as f:
            json.dump(self.conf, f)

    def get_current_page_courses(self, request_context, current_page):
        response = request_context.post(
            "https://learning.hzrs.hangzhou.gov.cn/api/index/index/SelectCourse",
            data=json.dumps({"type": self.course_type, "limit": 30, "page": current_page}),
            headers={"Content-Type": "application/json"}
        )

        assert response.ok

        self.last_page_num = response.json()['course']['last_page']

        for item in response.json()['course']['data']:
            course = Course(item['courseid'], item['coursename'])
            self.page_courses.append(course)

        self.filter_start_page_courses()

    def filter_start_page_courses(self):
        """断点续播，过滤当前页面已经播发过的课程"""
        if self.is_start_page and self.current_course_id:
            for i, course in enumerate(self.page_courses):
                if self.current_course_id == course.id:
                    index = i
                    self.page_courses = self.page_courses[index:]
                    break

    def play_current_page_courses(self, context):
        while len(self.page_courses) > 0:
            course = self.page_courses.pop()
            page = context.new_page()

            self.current_course_id = course.id
            self.current_course_name = course.name

            course.play(page)

    def run(self):
        with sync_playwright() as p:
            browser = p.webkit.launch(args=["--start-maximized"], headless=False, slow_mo=500)
            context = browser.new_context(storage_state="auth.json",
                                          viewport={"width": 1920, "height": 1080})  # 加载已保存的状态
            request_context = context.request

            try:
                while self.current_page_num < self.last_page_num:
                    self.get_current_page_courses(request_context, self.current_page_num)
                    self.play_current_page_courses(context)
                    self.current_page_num += 1
            finally:
                input('anything....')
                self.save_config()
                browser.close()


def main():
    player = Player()

    # 注册退出钩子
    import atexit
    atexit.register(player.save_config)

    # Ctrl+C 中断时也保存
    import signal
    import sys

    def handle_exit(signum, frame):
        print("捕获退出信号，正在保存配置...")
        player.save_config()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)

    player.run()


if __name__ == '__main__':
    main()
