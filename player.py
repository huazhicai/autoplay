# -*- coding:utf-8 -*-
import json
from playwright.sync_api import BrowserContext, sync_playwright

from course import Course, log

COURSE_TYPE = {'所有': 'all', '专业课程': "15", '行业公需': "16", '一般公需': "17"}


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
        try:
            response = context.request.post(
                "https://learning.hzrs.hangzhou.gov.cn/api/index/index/SelectCourse",
                data=json.dumps({"type": COURSE_TYPE[self.course_type], "limit": 30, "page": self.current_page}),
                headers={"Content-Type": "application/json"}
            )
            if not response.ok:
                log.error(f"API 请求失败: {response.status} {response.text()}")
                return False

            data = response.json()
            if "course" not in data:
                log.error("响应中缺少 'course' 字段; 可能是auth失效")
                return False

            data = response.json()['course']
            self.last_page = data.get('last_page', 10)

            self.course_list = [Course(item['courseid'], item['coursename']) for item in data['data']]

            # 断点续播：仅在开始页时过滤
            if self.is_start_page and self.current_course_id:
                self.course_list = self._filter_unwatched(self.course_list, self.current_course_id)

            self.is_start_page = False
            return True
        except Exception as e:
            log.error(f"获取课程列表失败: {str(e)}", exc_info=True)
            return False

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

    def login(self, page):
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

            page = context.new_page()
            try:
                self.login(page)
            except Exception:
                page.reload()
                self.login(page)

            while self.current_page <= self.last_page:
                self.fetch_courses(context)
                self.play_all_courses(context)
                self.current_page += 1
                # break

            input('anything....')
            page.close()
            browser.close()


if __name__ == '__main__':
    player = Player()
    player.run()
