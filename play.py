# -*- coding:utf-8 -*-
import json
import time
import typing
import logging
from playwright.sync_api import sync_playwright, BrowserContext

COURSE_TYPE = {'所有': 'all', '专业课程': "15", '行业公需': "16", '一般公需': "17"}

log = logging.getLogger(__name__)

log.setLevel(logging.DEBUG)


class Course:
    def __init__(self, course_id: str, course_name: str):
        self.id = course_id
        self.name = course_name

    @staticmethod
    def time_to_seconds(t):
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s

    @staticmethod
    def is_paused(page):
        return page.locator("#toPause").evaluate("el => getComputedStyle(el).display") == "none"

    @staticmethod
    def get_current_time(page):
        return page.locator("#currentTimeLabel").inner_text()

    @staticmethod
    def get_total_time(page):
        return page.locator("#totalTimeLabel").inner_text()

    def play(self, page):
        url = f"https://learning.hzrs.hangzhou.gov.cn/#/class?courseId={self.id}&coursetitle={self.name}"
        log.info(url)
        page.goto(url)
        page.on("dialog", lambda dialog: dialog.accept())
        page.wait_for_load_state('networkidle')

        if page.locator('iframe'):
            self.monitor_15_2_3(page)
        else:
            self.monitor_15_1(page)

        page.close()

    def monitor_15_1(self, page):
        try:
            # 尝试点击“是否继续学习”弹窗
            page.get_by_role("button", name="确定").click(timeout=2000)
            log.info("✅ 已点击‘确定’继续学习按钮")
        except Exception as e:
            log.debug(f"无‘继续学习’弹窗，跳过: {str(e)}")

        try:
            # 尝试点击播放按钮
            page.get_by_role("button", name="Play Video").click()
            log.info("✅ 已点击播放按钮")
        except Exception as e:
            log.debug(f"播放按钮未找到或超时，跳过: {str(e)}")

        # 设定总播放时长（例如40分钟）
        total_watch_time_ms = 40 * 60 * 1000
        check_interval_ms = 3000
        elapsed = 0

        # 播放控制按钮
        play_bar_button = page.locator('button.vjs-play-control')

        while elapsed < total_watch_time_ms:
            try:
                # 如果出现“确定”按钮的 HTML 弹窗，点击它
                dialog_button = page.get_by_role("button", name="确定").wait_for(state="visible", timeout=3000)
                dialog_button.click(force=True)
                log.info("✅ 已点击弹窗‘确定’按钮")
            except Exception as e:
                log.debug(f"[{time.strftime('%H:%M:%S')}] 无弹窗，继续播放:{str(e)}")

            try:
                # 监控播放控制按钮的状态
                title = play_bar_button.get_attribute("title")

                if title == "Play":
                    # 如果播放按钮是“Play”，表示暂停，点击播放
                    play_bar_button.click()
                    log.info("点击播放按钮")
                elif title == "Replay":
                    # 如果播放按钮是“Replay”，表示播放完毕，退出
                    log.info("播放结束，关闭页面")
                    break
            except Exception as e:
                log.debug(f"[{time.strftime('%H:%M:%S')}] 获取播放按钮 title 失败: {str(e)}")

            # 每3秒检查一次
            page.wait_for_timeout(check_interval_ms)
            elapsed += check_interval_ms

    def monitor_15_2_3(self, page):
        frame1 = page.locator('iframe').first.content_frame()
        frame2 = frame1.locator('iframe[name="course"]').content_frame()

        total_watch_time_ms = 50 * 60 * 1000
        check_interval_ms = 3000
        elapsed = 0

        max_seen_time = 0
        end_threshold = 9  # 允许9秒误差判断为“已播完”

        while elapsed < total_watch_time_ms:
            try:
                # 尝试点击“继续学习”的弹框
                try:
                    dialog_button = page.get_by_role("button", name="确定")
                    dialog_button.wait_for(state="visible", timeout=2000)
                    dialog_button.click()
                    log.debug("点击了‘继续学习’弹框")
                except:
                    pass  # 没弹出，无需处理

                paused = self.is_paused(frame2)
                current_time = self.get_current_time(frame2)
                total_time = self.get_total_time(frame2)

                current_sec = self.time_to_seconds(current_time)
                total_sec = self.time_to_seconds(total_time)

                log.debug(
                    f"当前时间: {current_time}（{current_sec}s），最大时间: {max_seen_time}s，总时长: {total_time}（{total_sec}s），暂停状态: {paused}")

                if current_sec > max_seen_time:
                    max_seen_time = current_sec
                    log.debug(f"更新最大播放时间为 {max_seen_time}s")

                # ✅ 播放完的判断（优先执行）
                if paused and max_seen_time >= total_sec - end_threshold:
                    log.debug("检测到视频播放完毕，准备退出。")
                    break

                # ⏸️ 中途暂停：点击播放
                if paused and current_sec < total_sec - end_threshold:
                    log.info("检测到中途暂停，点击播放。")
                    frame2.locator("#toPlay").click()

            except Exception as e:
                log.debug("元素可能不存在或页面出错:", str(e))

            page.wait_for_timeout(check_interval_ms)
            elapsed += check_interval_ms


class Player(object):
    def __init__(self, config_path='./config_define.json'):
        self.config_path = config_path
        self.config = self.load_config()
        self.headless = self.config.get('headless', False)
        self.current_page = self.config.get('current_page', 1)
        self.course_type = self.config['course_type']
        self.current_course_id = self.config.get('current_course_id')

        self.last_page = 10
        self.course_list: list[Course] = []
        self.is_start_page = True

    def load_config(self):
        with open(self.config_path, 'r', encoding="utf8") as f:
            return json.load(f)

    def save_config(self):
        self.config['current_course_id'] = self.current_course_id
        self.config['current_course_name'] = self.current_course_name
        self.config['current_page'] = self.current_page

        with open(self.config_path, 'w', encoding="utf8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def fetch_courses(self, context: BrowserContext):
        response = context.request.post(
            "https://learning.hzrs.hangzhou.gov.cn/api/index/index/SelectCourse",
            data=json.dumps({"type": COURSE_TYPE[self.course_type], "limit": 30, "page": self.current_page}),
            headers={"Content-Type": "application/json"}
        )
        assert response.ok
        log.debug(response.json())

        data = response.json()['course']
        self.last_page = data['last_page']

        self.course_list = [Course(item['courseid'], item['coursename']) for item in data['data']]

        if self.is_start_page and self.current_course_id:
            self.course_list = self._filter_unwatched(self.course_list, self.current_course_id)

        self.is_start_page = False

    def _filter_unwatched(self, courses: list[Course], start_id: str):
        """断点续播，过滤当前页面已经播发的课程"""
        for i, course in enumerate(courses):
            if course.id == start_id:
                return courses[i:]
        return courses

    def play_all_courses(self, context: BrowserContext):
        for course in self.course_list:
            self.current_course_id = course.id
            self.current_course_name = course.name
            self.save_config()
            course.play(context.new_page())

    def login(self, context):
        page = context.new_page()
        page.goto("https://learning.hzrs.hangzhou.gov.cn/#/")
        page.get_by_role("button", name="学员登录").click()
        page.get_by_text("在线学习系统").click()
        page.get_by_text("网络课程").first.click()
        page.click("div.el-select__placeholder:has-text('--所有--')")
        page.click(f"li:has-text(\'{self.course_type}\')")
        page.get_by_role("button", name="查询").click()
        return page

    def run(self):
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=self.headless, args=["--start-maximized"], slow_mo=100)
            context = browser.new_context(storage_state="auth.json", viewport={"width": 1920, "height": 1080})

            page = self.login(context)

            while self.current_page <= self.last_page:
                self.fetch_courses(context)
                self.play_all_courses(context)
                self.current_page += 1
                time.sleep(6)

            input('anything....')
            page.close()
            browser.close()


if __name__ == '__main__':
    player = Player()
    player.run()
