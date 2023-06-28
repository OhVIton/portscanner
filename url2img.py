from selenium import webdriver
import chromedriver_binary
from selenium.common.exceptions import InvalidArgumentException, WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from http.client import BadStatusLine
from requests.adapters import ProtocolError, ConnectionError, SSLError
import time

import logging

from typing import Union

from concurrent.futures import ThreadPoolExecutor

import os
from dotenv import load_dotenv

import logging

load_dotenv()
SCREENSHOT_SAVE_PATH = os.environ.get("SCREENSHOT_SAVE_PATH")
LOG_PATH = os.environ.get("LOG_PATH")

logger = logging.getLogger("portscanner")


options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument('--proxy-server="direct://"')
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument(
    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
)
options.page_load_strategy = "eager"
options.set_capability("acceptInsecureCerts", True)


def _url2img(url, fname):
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1440, 960)
    logger.debug(
        f"[url2img] started chrome webdriver with options: {options}"
    )
    try:
        if not url.startswith("http") and not url.startswith("https"):
            if url.endswith(":443"):
                logger.info(f"[url2img] complement url with https://")
                query_url = "https://" + url
            else:
                logger.info(f"[url2img] complement url http://")
                query_url = "http://" + url

        else:
            query_url = url

        logger.info(f"[url2img] GET {query_url}")
        try:
            # check if the page is accessible
            res = requests.get(query_url, verify=False, timeout=10)
            if res.text:
                driver.get(query_url)
                # driver.execute_script("document.body.style.zoom= '50%';")

                wait_time = 10
                try:
                    if os.environ.get("SCREENSHOT_WAIT_TIME"):
                        wait_time = int(os.environ.get("SCREENSHOT_WAIT_TIME"))
                except ValueError:
                    pass

                logger.info(f"[url2img] {query_url} waiting {wait_time} seconds....")
                time.sleep(wait_time)
                savepath = f"{SCREENSHOT_SAVE_PATH}/{fname}.png"
                logger.info(
                    f"[url2img] save the screenshot of {query_url} as {savepath}"
                )
                driver.save_screenshot(savepath)
                return True
            else:
                return False
        except (BadStatusLine, ProtocolError, ConnectionError, SSLError) as e:
            logger.info(
                f"[url2img] {query_url} can't be connected by {e}. skipped."
            )
            return False
        except Exception as e:
            logger.info(
                f"[url2img] {query_url} exception {e}. skipped."
            )
            return False


    except InvalidArgumentException as iae:
        # print("\n\033[31m URL may be incorrect\033[0m")
        logger.error(f"[url2img] URL may be incorrect.")
        return False
    except WebDriverException as wde:
        # print("\n\033[31m URL doesn't have any web interface \033[0m")
        logger.info(
            f"[url2img] {url} doesn't have any web interface."
        )
        return False
    except Exception as e:
        logger.error(f"[url2img] {e}")
        return False


def url2img(url: Union[str, list], fname: Union[str, list]) -> dict:
    """
    Get a screenshot from a website

    parameters
    ----------
    url: str
        starts with http:// or https://
    fname: str

    returns
    ----------
    {fname: True|False, ...}
    """

    if type(url) == str:
        return _url2img(url, fname)

    elif type(url) == list:
        futures = dict()

        max_workers = 3
        try:
            if os.environ.get("SCREENSHOT_THREADS_NUM"):
                max_workers = int(os.environ.get("SCREENSHOT_THREADS_NUM"))
                if max_workers <= 0:
                    max_workers = 3
        except ValueError:
            pass

        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for t_idx in range(0, len(url), max_workers):
                    futures[fname[t_idx]] = executor.submit(
                        _url2img, url[t_idx], fname[t_idx]
                    )

                    for m_idx in range(1, max_workers):
                        if t_idx + m_idx < len(url):
                            futures[fname[t_idx + m_idx]] = executor.submit(
                                _url2img, url[t_idx + m_idx], fname[t_idx + m_idx]
                            )
            return futures
        except Exception as e:
            logger.error(f"[url2img] {e}")
            return {"": False}
