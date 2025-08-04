# -*- coding:utf-8 -*-
import time
import logging

from typing import Optional
from playwright.sync_api import Page, Frame, TimeoutError, expect

# 创建一个logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)  # 设置日志级别为DEBUG，这样可以捕获所有级别的日志

# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 定义handler的输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 给logger添加handler
log.addHandler(fh)
log.addHandler(ch)


class Course:
    def __init__(self, course_id: str, course_name: str):
        self.id = course_id
        self.name = course_name

    @staticmethod
    def time_to_seconds(t: str) -> int:
        """将时间字符串 'HH:MM:SS' 转换为秒数"""
        try:
            h, m, s = map(int, t.strip().split(":"))
            return h * 3600 + m * 60 + s
        except Exception as e:
            log.warning(f"时间解析失败: {t}, 错误: {e}")
            return 0

    @staticmethod
    def is_paused(frame) -> bool:
        """检查播放是否暂停"""
        try:
            display = frame.locator("#toPause").evaluate(
                "el => getComputedStyle(el).display"
            )
            return display == "none"
        except Exception as e:
            log.debug(f"无法获取暂停状态: {e}")
            return True  # 默认视为暂停（安全策略）

    @staticmethod
    def is_paused_2(frame) -> bool:
        """检查播放是否暂停"""
        try:
            display = frame.locator("#media1_jwplayer_display_iconBackground").evaluate(
                "el => getComputedStyle(el).display"
            )
            return display == "block"
        except Exception as e:
            log.debug(f"无法获取暂停状态: {e}")
            return True  # 默认视为暂停（安全策略）

    @staticmethod
    def get_current_time(frame) -> Optional[str]:
        """获取当前播放时间"""
        try:
            text = frame.locator("#currentTimeLabel").inner_text(timeout=3000)
            return text.strip()
        except TimeoutError:
            log.debug("获取当前时间超时")
            return None

    @staticmethod
    def get_total_time(frame) -> Optional[str]:
        """获取总时长"""
        try:
            text = frame.locator("#totalTimeLabel").inner_text(timeout=3000)
            return text.strip()
        except TimeoutError:
            log.debug("获取总时长超时")
            return None

    def play(self, page: Page):
        url = f"https://learning.hzrs.hangzhou.gov.cn/#/class?courseId={self.id}&coursetitle={self.name}"
        log.info(url)
        page.goto(url)
        page.on("dialog", lambda dialog: dialog.accept())  # 自动接受所有弹窗

        try:
            page.wait_for_load_state('networkidle', timeout=10000)
        except TimeoutError:
            log.warning("页面加载超时，但仍继续执行...")

        # 判断是否包含 iframe（区分版本 15.1 / 15.2.3）
        if page.locator('#hls_html5_api').count() > 0:
            self.monitor_15_1(page)
        else:
            frame = page.frame_locator('iframe').frame_locator('iframe[name="course"]')
            if frame.locator("#currentPageLabel").count() > 0:
                self.monitor_15_2(page)
            elif frame.locator("#initPanel").count() > 0:
                self.monitor_15_3(page)
            else:
                log.warning('未识别到监控选择器，查看debug_screenshot1.png')
                page.screenshot(path="debug_screenshot.png")  # 截图辅助调试

        page.close()

    def monitor_15_1(self, page: Page):
        log.info("检测到模式 15.1 监控")

        # 尝试点击“继续学习”弹窗
        self._handle_dialog_button(page, "确定", timeout=2000)

        # 尝试点击 Play Video 按钮
        try:
            play_button = page.get_by_role("button", name="Play Video")
            expect(play_button).to_be_visible(timeout=2000)
            play_button.click()
            log.info("已点击播放按钮")
        except TimeoutError:
            page.screenshot(path="debug_screenshot1.png")  # 截图辅助调试
            log.warning("1、未找到播放按钮，可以尝试手动点击播放")

        # 播放控制按钮（VJS 播放器）
        play_control = page.locator('button.vjs-play-control')

        total_watch_time = 70 * 60 * 1000
        start_time = time.time() * 1000

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                # 处理中途弹窗
                self._handle_dialog_button(page, "确定", timeout=3000)

                # 获取播放按钮 title
                title = play_control.get_attribute("title", timeout=2000)
                if title == "Play":
                    log.info("检测到暂停，点击继续播放")
                    play_control.click(force=True)
                elif title == "Replay":
                    log.info("视频播放完毕，退出循环")
                    break
            except Exception as e:
                log.debug(f"监控播放状态异常: {str(e)}")

    def monitor_15_2(self, page: Page):
        log.info("检测到模式 15.2 监控")
        frame = page.frame_locator('iframe').frame_locator('iframe[name="course"]')
        try:
            frame.locator('#nextButton').click()
            page.wait_for_timeout(5000)
            frame.locator('#previousButton').click()
            log.info("已点击播放按钮")
        except Exception as e:
            frame.locator("#mediaMaskBg").click()
            page.wait_for_timeout(5000)
            frame.locator("#mediaMaskBg").click()
            page.screenshot(path="debug_screenshot2.png")  # 截图辅助调试
            log.warning("2、自动播发失败，可以尝试手动点击播放")

        total_watch_time = 60 * 60 * 1000  # 60分钟
        start_time = time.time() * 1000

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                self._handle_dialog_button(page, "确定", timeout=2000)

                current_page_label = frame.locator("#currentPageLabel").inner_text(timeout=3000)
                total_page_label = frame.locator("#totalPageLabel").inner_text(timeout=3000)
                paused_2 = self.is_paused_2(frame)

                if paused_2:
                    if current_page_label == total_page_label:
                        page.wait_for_timeout(2 * 60 * 1000)
                        break
                    frame.locator('#nextButton').click()
            except Exception as e:
                log.debug(f"监控过程中发生异常: {str(e)}")

            page.wait_for_timeout(1000)

    def monitor_15_3(self, page: Page):
        log.info("检测到模式 15.3 监控")
        frame = page.frame_locator('iframe').frame_locator('iframe[name="course"]')
        try:
            frame.locator('#mediaMask').click()  # 恢复秩序
            frame.locator('#mediaMask').click()  # 开始播放
            log.info("已点击播放按钮")
        except Exception as e:
            log.warning('点击播放失败，请手动点击开始观看')
            page.screenshot(path="debug_screenshot3.png")  # 截图辅助调试

        total_watch_time = 60 * 60 * 1000  # 60分钟
        start_time = time.time() * 1000

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                # 处理中途弹窗
                self._handle_dialog_button(page, "确定", timeout=3000)

                current_time_str = self.get_current_time(frame)
                total_time_str = self.get_total_time(frame)

                if current_time_str == total_time_str:
                    break

                if self.is_paused(frame):
                    frame.locator("#toPlay").click(timeout=3000)

            except Exception as e:
                log.error(f"监控过程中发生异常: {str(e)}")

            page.wait_for_timeout(1000)

    def _handle_dialog_button(self, page, button_text: str, timeout: int = 3000):
        """通用处理弹窗按钮"""
        try:
            button = page.get_by_role("button", name=button_text)
            expect(button).to_be_visible(timeout=timeout)
            button.click(force=True)
            log.info(f"已点击弹窗按钮: '{button_text}'")
        except TimeoutError:
            log.debug(f"未出现 '{button_text}' 弹窗，跳过")
        except Exception as e:
            log.debug(f"点击 '{button_text}' 时出错: {e}")
