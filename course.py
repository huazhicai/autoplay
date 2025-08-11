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
            frame.locator("#toPause").wait_for(timeout=5000)  # 等待最多 5 秒
            display = frame.locator("#toPause").evaluate("el => getComputedStyle(el).display")
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
            text = frame.locator("#currentTimeLabel").inner_text()
            return text.strip()
        except TimeoutError:
            log.debug("获取当前时间超时")
            return None

    @staticmethod
    def get_total_time(frame) -> Optional[str]:
        """获取总时长"""
        try:
            text = frame.locator("#totalTimeLabel").inner_text()
            return text.strip()
        except TimeoutError:
            log.debug("获取总时长超时")
            return None

    def select_monitor(self, page):
        try:
            # 判断是否包含 iframe（区分版本 15.1 / 15.2.3）
            if page.locator('#hls_html5_api').count() > 0:
                self.monitor_15_1(page)
            else:
                frame = page.frame_locator('iframe').frame_locator('iframe[name="course"]')
                if frame.locator("#media1_jwplayer_display_iconBackground").count() > 0:
                    self.monitor_15_2(page)
                elif frame.locator("#currentPageLabel").count() > 0:
                    self.monitor_15_4(page)
                elif frame.locator("#initPanel").count() > 0:
                    self.monitor_15_3(page)
                else:
                    log.warning('未识别到监控选择器，查看debug_screenshot.png')
                    page.screenshot(path="debug_screenshot.png")  # 截图辅助调试
            return True
        except Exception as e:
            page.screenshot(path="debug_screenshot.png")  # 截图辅助调试
            log.warning(f'select_monitor failed: {str(e)}')
            return False

    def play(self, page: Page):
        # url = f"https://learning.hzrs.hangzhou.gov.cn/#/class?courseId={self.id}&coursetitle={self.name}"
        url = "https://learning.hzrs.hangzhou.gov.cn/#/class?courseId=66841&coursetitle=双碳目标下智能电网的定位与演变(中)"
        log.info(url)
        page.goto(url)
        page.on("dialog", lambda dialog: dialog.accept())  # 自动接受所有弹窗

        try:
            page.wait_for_load_state('networkidle')
        except TimeoutError:
            log.warning("页面加载超时，但仍继续执行...")

        if not self.select_monitor(page):
            page.reload()  # 页面卡死，刷新
            page.wait_for_timeout(10000)
            if not self.select_monitor(page):
                log.warning(f'页面加载失败，播放下一个视频')

        page.close()

    def monitor_15_1(self, page: Page):
        log.info("检测到模式 15.1 监控")

        # 尝试点击“继续学习”弹窗
        self._handle_dialog_button(page, "确定")
        try:
            play_button = page.get_by_role("button", name="Play Video")
            expect(play_button).to_be_visible()
            play_button.click()
            log.info("已点击播放按钮")
        except TimeoutError as e:
            page.screenshot(path="debug_screenshot1.png")  # 截图辅助调试
            log.warning(f"1、未找到播放按钮 debug_screenshot1.png，可以尝试手动点击播放: str({e}")

        # 播放控制按钮（VJS 播放器）
        play_control = page.locator('button.vjs-play-control')

        total_watch_time = 70 * 60 * 1000
        start_time = time.time() * 1000

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                # 处理中途弹窗
                self._handle_dialog_button(page, "确定")

                # 获取播放按钮 title
                title = play_control.get_attribute("title")
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
        self._handle_dialog_button(page, "确定")
        frame = page.frame_locator('iframe').frame_locator('iframe[name="course"]')
        try:
            frame.locator('#nextButton').wait_for(state="visible")
            frame.locator('#nextButton').click()
            page.wait_for_timeout(5000)
            frame.locator('#previousButton').click()
            log.info("已点击播放按钮")
        except Exception as e:
            frame.locator('#mediaMaskBg').wait_for(state="visible")
            frame.locator("#mediaMaskBg").click()
            page.wait_for_timeout(5000)
            frame.locator("#mediaMaskBg").click()
            page.screenshot(path="debug_screenshot2.png")  # 截图辅助调试
            log.warning(f"2、自动播放失败 debug_screenshot2.png，可以尝试手动点击播放: {str(e)}")

        total_watch_time = 60 * 60 * 1000  # 60分钟
        start_time = time.time() * 1000

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                self._handle_dialog_button(page, "确定")

                current_page_label = frame.locator("#currentPageLabel").inner_text()
                total_page_label = frame.locator("#totalPageLabel").inner_text()
                paused_2 = self.is_paused_2(frame)

                if paused_2:
                    if current_page_label == total_page_label:
                        page.wait_for_timeout(2 * 60 * 1000)
                        log.info("视频播放完毕，退出循环")
                        break
                    frame.locator('#nextButton').click()
                    log.info("检测到暂停，点击继续播放")
            except Exception as e:
                log.debug(f"监控过程中发生异常: {str(e)}")

    def monitor_15_3(self, page: Page):
        log.info("检测到模式 15.3 监控")
        self._handle_dialog_button(page, "确定")
        frame = page.frame_locator('iframe').frame_locator('iframe[name="course"]')
        try:
            frame.locator('#mediaMask').wait_for(state="visible")
            frame.locator('#mediaMask').click()
            frame.locator('#mediaMask').click()  # 开始播放
            log.info("已点击播放按钮")
        except Exception as e:
            log.warning(f'点击播放失败 debug_screenshot3.png，请手动点击开始观看:{str(e).encode("ascii", "ignore").decode()}')
            page.screenshot(path="debug_screenshot3.png")  # 截图辅助调试

        total_watch_time = 60 * 60 * 1000  # 60分钟
        start_time = time.time() * 1000

        max_seen_time = 0
        end_threshold = 9

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                # 处理中途弹窗
                self._handle_dialog_button(page, "确定")

                current_time_str = self.get_current_time(frame)
                total_time_str = self.get_total_time(frame)
                current_sec = self.time_to_seconds(current_time_str)
                total_sec = self.time_to_seconds(total_time_str)
                if current_sec > max_seen_time:
                    max_seen_time = current_sec

                if current_time_str == total_time_str:
                    log.info("视频播放完毕，退出循环")
                    break

                paused = self.is_paused(frame)
                if max_seen_time >= total_sec - end_threshold:
                    log.info(f"检测到播放完成，退出")
                    break

                if paused and current_sec < total_sec - end_threshold:
                    try:
                        frame.locator('#toPlay').wait_for(state="visible", timeout=1000)
                        frame.locator("#toPlay").click()
                        log.info(f"检测到暂停，已点击播放")
                    except Exception as e:
                        pass
            except Exception as e:
                log.error(f"监控过程中发生异常: {str(e)}")

    def monitor_15_4(self, page: Page):
        log.info("检测到模式 15.4 监控")
        self._handle_dialog_button(page, "确定")
        frame = page.frame_locator('iframe').frame_locator('iframe[name="course"]')
        try:
            frame.locator('#toPlay').wait_for(state="visible", timeout=3000)
            frame.locator('#toPlay').click()
            log.info("已点击播放按钮")
        except Exception as e:
            page.screenshot(path="debug_screenshot4.png")  # 截图辅助调试
            log.warning(f"2、自动播放失败 debug_screenshot2.png，可以尝试手动点击播放: {str(e)}")

        total_watch_time = 60 * 60 * 1000  # 60分钟
        start_time = time.time() * 1000
        max_page = '1'

        while (time.time() * 1000 - start_time) < total_watch_time:
            try:
                self._handle_dialog_button(page, "确定")

                paused = self.is_paused(frame)

                if paused:
                    frame.locator('#toPlay').wait_for(state="visible", timeout=3000)
                    frame.locator("#toPlay").click()
                    log.info(f"检测到暂停，已点击播放")

                current_page_label = frame.locator("#currentPageLabel").inner_text()
                total_page_label = frame.locator("#totalPageLabel").inner_text()

                if int(current_page_label) > int(max_page):
                    max_page = current_page_label

                if max_page == total_page_label and int(current_page_label) < int(max_page):
                    log.info(f"检测到播放完成，退出")
                    break
            except Exception as e:
                log.debug(f"监控过程中发生异常: {str(e)}")

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
