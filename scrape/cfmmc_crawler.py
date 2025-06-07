import asyncio
import time
import tempfile
import logging
from typing import Optional, Tuple
import pandas as pd
from DrissionPage import Chromium, ChromiumOptions
import ddddocr
from pathlib import Path

logger = logging.getLogger(__name__)


class CFMMCLoginError(Exception):
    """CFMMC登录错误基类"""
    pass


class CFMMCCredentialsError(CFMMCLoginError):
    """用户名密码错误"""
    pass


class CFMMCVerificationCodeError(CFMMCLoginError):
    """验证码错误"""
    pass


class CFMMCCrawler:
    """CFMMC持仓信息爬虫类"""

    def __init__(self, headless: bool = True):
        self.ocr = ddddocr.DdddOcr()
        self.max_retries = 10
        self.login_timeout = 30
        self.download_timeout = 60
        self.headless = headless

    async def get_position_data(self,
                                trade_date: str,
                                username: str,
                                password: str) -> Optional[pd.DataFrame]:
        """
        获取指定日期的持仓数据

        参数:
            trade_date: 交易日期，格式YYYY-MM-DD
            username: CFMMC用户名
            password: CFMMC密码

        返回:
            pd.DataFrame: 持仓数据，失败时返回None

        抛出异常:
            CFMMCCredentialsError: 用户名密码错误
            CFMMCVerificationCodeError: 验证码错误
            CFMMCLoginError: 其他登录错误
        """
        browser = None
        temp_dir = None

        try:
            temp_dir = tempfile.mkdtemp()
            browser = self._create_browser(temp_dir)
            crawler = browser.latest_tab

            login_success = await self._login_with_retry(crawler, username, password)
            if not login_success:
                return None

            file_path = await self._download_position_file(crawler, trade_date, temp_dir)
            if not file_path:
                return None

            df = await self._read_position_file(file_path)
            return df

        except (CFMMCCredentialsError, CFMMCVerificationCodeError, CFMMCLoginError):
            raise
        except Exception as crawler_error:
            logger.error(f"获取持仓数据时出现异常: {crawler_error}")
            return None

        finally:
            if browser:
                try:
                    browser.quit()
                except Exception as close_error:
                    logger.warning(f"关闭浏览器时出现警告: {close_error}")

            if temp_dir:
                await self._cleanup_temp_files(temp_dir)

    def _create_browser(self, download_dir: str) -> Chromium:
        """创建浏览器实例"""
        try:
            if self.headless:
                co = ChromiumOptions().headless()
                browser = Chromium(co)
            else:
                browser = Chromium()

            browser.set.download_path(download_dir)
            return browser

        except Exception as browser_error:
            raise CFMMCLoginError(f"浏览器启动失败: {browser_error}")

    async def _login_with_retry(self, crawler, username: str, password: str) -> bool:
        """带重试的登录流程"""
        for attempt in range(self.max_retries):
            try:
                crawler.get('https://investorservice.cfmmc.com')
                await asyncio.sleep(1)

                await self._wait_for_page_load(crawler)

                success, error_type = await self._perform_login(crawler, username, password)

                if success:
                    return True

                if error_type == 'credentials_error':
                    raise CFMMCCredentialsError("用户名或密码错误")

                elif error_type == 'verification_error':
                    if attempt >= self.max_retries - 1:
                        raise CFMMCVerificationCodeError("验证码识别失败，重试次数已达上限")
                    await asyncio.sleep(1)
                    continue

                else:
                    if attempt >= self.max_retries - 1:
                        break
                    await asyncio.sleep(1)
                    continue

            except (CFMMCCredentialsError, CFMMCVerificationCodeError):
                raise
            except Exception as login_error:
                if attempt >= self.max_retries - 1:
                    raise CFMMCLoginError(f"登录过程出现异常: {login_error}")
                await asyncio.sleep(2)

        raise CFMMCLoginError("登录失败，已达到最大重试次数")

    @staticmethod
    async def _wait_for_page_load(crawler):
        """等待页面关键元素加载完成"""
        max_wait = 10
        start_time = time.time()

        while time.time() - start_time < max_wait:
            user_id_input = crawler.ele('@name=userID')
            password_input = crawler.ele('@name=password')
            verification_code_input = crawler.ele('@name=vericode')
            verification_img = crawler.ele('@id=imgVeriCode')

            if all([user_id_input, password_input, verification_code_input, verification_img]):
                await asyncio.sleep(0.5)
                return True

            await asyncio.sleep(0.5)

        return False

    async def _perform_login(self, crawler, username: str, password: str) -> Tuple[bool, str]:
        """执行单次登录操作"""
        try:
            user_id_input = crawler.ele('@name=userID')
            password_input = crawler.ele('@name=password')
            verification_code_input = crawler.ele('@name=vericode')

            if not all([user_id_input, password_input, verification_code_input]):
                return False, 'unknown_error'

            verification_code = await self._get_verification_code(crawler)
            if not verification_code:
                return False, 'verification_error'

            user_id_input.clear()
            user_id_input.input(username)

            password_input.clear()
            password_input.input(password)

            verification_code_input.clear()
            verification_code_input.input(verification_code)

            submit_btn = crawler.ele('@type=submit')
            if not submit_btn:
                return False, 'unknown_error'

            submit_btn.click()
            await asyncio.sleep(1)

            return await self._verify_login_success(crawler)

        except Exception:
            return False, 'unknown_error'

    async def _get_verification_code(self, crawler) -> Optional[str]:
        """获取并识别验证码"""
        max_attempts = 10

        for attempt in range(max_attempts):
            try:
                if attempt > 0:
                    await asyncio.sleep(1)

                verification_img = crawler.ele('@id=imgVeriCode')
                if not verification_img:
                    if attempt < max_attempts - 1:
                        continue
                    return None

                verification_img_src = verification_img.src()
                if not verification_img_src:
                    if attempt < max_attempts - 1:
                        try:
                            verification_img.click()
                            await asyncio.sleep(1)
                        except Exception:
                            pass
                        continue
                    return None

                ocr_result = self.ocr.classification(verification_img_src)
                if ocr_result and len(ocr_result.strip()) > 0:
                    return ocr_result.strip()
                else:
                    if attempt < max_attempts - 1:
                        continue

            except Exception:
                if attempt < max_attempts - 1:
                    continue

        return None

    @staticmethod
    async def _verify_login_success(crawler) -> Tuple[bool, str]:
        """验证登录是否成功"""
        try:
            page_text = crawler.html

            if "用户名或密码错误" in page_text:
                return False, 'credentials_error'

            if any(error in page_text for error in ["Invalid Verification Code", "验证码错误", "验证码不正确"]):
                return False, 'verification_error'

            logout_btn = crawler.ele('@name=logout')
            if logout_btn:
                return True, 'success'

            download_btn = crawler.ele('#myDownload')
            if download_btn:
                return True, 'success'

            return False, 'unknown_error'

        except Exception:
            return False, 'unknown_error'

    async def _download_position_file(self, crawler, trade_date: str, download_dir: str) -> Optional[str]:
        """下载持仓文件"""
        try:
            date_input = crawler.ele('@name=tradeDate')
            if not date_input:
                return None

            date_input.clear()
            date_input.input(trade_date)

            submit_btn = crawler.ele('@value=提交')
            if submit_btn:
                submit_btn.click()
                await asyncio.sleep(1)

            download_btn = crawler.ele('#myDownload')
            if not download_btn:
                return None

            download_btn.click()

            file_path = await self._wait_for_download(download_dir)
            return file_path

        except Exception:
            return None

    async def _wait_for_download(self, download_dir: str) -> Optional[str]:
        """等待文件下载完成"""
        start_time = time.time()

        while time.time() - start_time < self.download_timeout:
            try:
                download_path = Path(download_dir)
                files = list(download_path.glob("*.xls*"))
                actual_files = [f for f in files if not f.name.endswith('.crdownload')]

                if actual_files:
                    return str(actual_files[0])

                await asyncio.sleep(1)

            except Exception:
                await asyncio.sleep(1)

        return None

    async def _read_position_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """读取持仓文件为DataFrame"""
        try:
            df = pd.read_excel(file_path, sheet_name='持仓明细', skiprows=9)

            if df.empty:
                return pd.DataFrame()

            df = await self._process_position_data(df)
            return df

        except Exception:
            try:
                df = pd.read_excel(file_path, skiprows=9)
                df = await self._process_position_data(df)
                return df
            except Exception:
                return None

    @staticmethod
    async def _process_position_data(df: pd.DataFrame) -> pd.DataFrame:
        """处理持仓数据"""
        try:
            df = df.dropna(how='all')
            return df
        except Exception:
            return df

    @staticmethod
    async def _cleanup_temp_files(temp_dir: str):
        """清理临时文件"""
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


# 创建全局爬虫实例
cfmmc_crawler = CFMMCCrawler()


async def get_user_position_data(trade_date: str,
                                 username: str,
                                 password: str) -> Optional[pd.DataFrame]:
    """
    获取用户持仓数据的便捷函数

    参数:
        trade_date: 交易日期，格式YYYY-MM-DD
        username: CFMMC用户名
        password: CFMMC密码

    返回:
        pd.DataFrame: 持仓数据，失败时返回None
    """
    return await cfmmc_crawler.get_position_data(trade_date, username, password)