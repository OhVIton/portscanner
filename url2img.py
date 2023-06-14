from selenium import webdriver
import chromedriver_binary
from selenium.common.exceptions import InvalidArgumentException, WebDriverException
import time

import logging
import datetime

from typing import Union

from concurrent.futures import ThreadPoolExecutor

import os
from dotenv import load_dotenv

now = datetime.datetime.now().strftime("%Y-%m-%d.%H-%M-%S-%f")
SCREENSHOT_SAVE_PATH = os.environ.get("SCREENSHOT_SAVE_PATH")
LOG_PATH = os.environ.get("LOG_PATH")
os.makedirs(SCREENSHOT_SAVE_PATH, exist_ok=True)
os.makedirs(LOG_PATH, exist_ok=True)
logging.basicConfig(filename=f"{LOG_PATH}/{now}.log", level=logging.INFO)


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


def _url2img(url, fname):
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(720, 480)
    logging.debug(
        f"{datetime.datetime.now()} [url2img] started chrome webdriver with options: {options}"
    )
    try:
        if not url.startswith("http") and not url.startswith("https"):
            logging.info(f"{datetime.datetime.now()} [url2img] complement url")
            query_url = "http://" + url
        else:
            query_url = url

        logging.info(f"{datetime.datetime.now()} [url2img] GET {query_url}")
        driver.get(query_url)
        driver.execute_script("document.body.style.zoom= '50%';")

        logging.info(f"{datetime.datetime.now()} [url2img] waiting 10 seconds....")
        time.sleep(10)
        # if the page is blank, return false
        if (
            driver.page_source
            == '<html><head></head><body style="zoom: 50%;"></body></html>'
        ):
            logging.info(
                f"{datetime.datetime.now()} [url2img] {query_url} was a blank page. skipped."
            )
            return False
        savepath = f"{SCREENSHOT_SAVE_PATH}/{fname}.png"
        logging.info(
            f"{datetime.datetime.now()} [url2img] save the screenshot of {query_url} as {savepath}"
        )
        driver.save_screenshot(savepath)
        return True
    except InvalidArgumentException as iae:
        # print("\n\033[31m URL may be incorrect\033[0m")
        logging.error(f"{datetime.datetime.now()} [url2img] URL may be incorrect.")
        return False
    except WebDriverException as wde:
        # print("\n\033[31m URL doesn't have any web interface \033[0m")
        logging.info(
            f"{datetime.datetime.now()} [url2img] {url} doesn't have any web interface."
        )
        return False
    except Exception as e:
        logging.error(f"{datetime.datetime.now()} [url2img] {e}")
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
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                for t_idx in range(0, len(url), 3):
                    futures[fname[t_idx]] = executor.submit(
                        _url2img, url[t_idx], fname[t_idx]
                    )
                    if t_idx + 1 < len(url):
                        futures[fname[t_idx + 1]] = executor.submit(
                            _url2img, url[t_idx + 1], fname[t_idx + 1]
                        )
                    if t_idx + 2 < len(url):
                        futures[fname[t_idx + 2]] = executor.submit(
                            _url2img, url[t_idx + 2], fname[t_idx + 2]
                        )
            return futures
        except Exception as e:
            logging.error(f"{datetime.datetime.now()} [url2img] {e}")
            return {"": False}
