# -*- coding:utf-8 -*-
import time

from playwright.sync_api import sync_playwright
import re
import json
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright

COURSE_TYPE = {'所有': 'all', '专业课程': 15, '行业公需': 16, '一般公需': 17}
pages = 33


class Player(object):
    def __init__(self):
        self.headless = False
        self.course_type = None
        self.current_course_id = None
        self.current_course_name = None
        self.current_page = None
        self.last_page = 10

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
        self.current_page = self.conf.get('current_page')

    def save_config(self):
        self.conf['current_course_id'] = self.current_course_id
        self.conf['current_course_name'] = self.current_course_name
        self.conf['current_page'] = self.current_page

        with open(self.conf_file, 'w', encoding="utf8") as f:
            json.dump(self.conf, f)

    def on_response(self, response):
        print(response.url)
        if response.status == 200 and 'SelectCourse' in response.url:
            urls = []
            print(response.json())
            for item in response.json()['course']['data']:
                courseid, coursename = item['courseid'], item['coursename']
                url = f"https://learning.hzrs.hangzhou.gov.cn/#/class?courseId={courseid}&coursetitle={coursename}"
                print(url)
                if url not in urls:
                    urls.append(url)

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

    def run(self):
        with sync_playwright() as p:
            browser = p.webkit.launch(args=["--start-maximized"], headless=False, slow_mo=500)
            context = browser.new_context(storage_state="auth.json",
                                          viewport={"width": 1920, "height": 1080})  # 加载已保存的状态

            # 创建 request client
            request_context = context.request

            page = context.new_page()
            page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")

            page.get_by_role("button", name="学员登录").click()
            page.get_by_text("在线学习系统").click()

            # 发起 POST 请求
            page.wait_for_timeout(5000)
            response = request_context.post(
                "https://learning.hzrs.hangzhou.gov.cn/api/index/index/SelectCourse",
                data={"type": "16", 'limit': 30, 'page': 10},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    # 通常无需 Authorization，cookie 已包含在 auth.json 里
                }
            )

            api_response = page.evaluate("""async () => {
                const response = await fetch("https://learning.hzrs.hangzhou.gov.cn/api/index/index/SelectCourse", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: "type=11&limit=30&page=10"
                });
                return response.json();
            }""")
            print(api_response)

            self.current_page = response.json()['course']['current_page']
            print(response.json())

            for item in response.json()['course']['data']:
                self.current_course_id = item['courseid']
                self.current_course_name = item['coursename']
                page = context.new_page()
                self.play_course(page)

            # page = context.new_page()
            # page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")       # 已是登录态
            #
            # page.get_by_text("网络课程").first.click()
            #
            # page.click("div.el-select__placeholder:has-text('--所有--')")
            # page.wait_for_timeout(500)  # 等待0.5秒
            # page.click("li:has-text('行业公需')")
            #
            # page.get_by_role("button", name="查询").click()
            # page.on('response', self.on_response)

            # current_page = 1
            # while current_page < total_page:
            #     page.wait_for_timeout(500)
            #     page.get_by_role("listitem", name=f"第 {current_page} 页").click()
            # page.on('response', on_response)
            # page.wait_for_load_state('networkidle')

            input('anything....')
            browser.close()


if __name__ == '__main__':
    player = Player()
    player.run()
