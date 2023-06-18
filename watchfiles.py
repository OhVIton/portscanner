import time
import os

import logging

import requests
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

if not os.environ.get("SFTP_ONDEMAND_PATH"):
    from dotenv import load_dotenv
    load_dotenv()

SFTP_ONDEMAND_PATH = os.environ.get("SFTP_ONDEMAND_PATH")
SCANNER_API_URL = "http://127.0.0.1:8000"


while True:
    ondemand_path = Path(SFTP_ONDEMAND_PATH)
    ip_done_txts = tuple(f for f in ondemand_path.glob("*.txt"))
    if ip_done_txts:
        max_workers = 3
        futures = dict()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for ip_txt in ip_done_txts:
                with open(ip_txt, "r") as f:
                    ip = f.read().rstrip()
                    futures[ip_txt] = executor.submit(requests.get, f"{SCANNER_API_URL}/scan?ip={ip}")
                    ip_txt.rename(str(ip_txt) + ".done")
            try:
                for key,val in futures.items():
                    res = val.result()
                    if res.status_code == 200:
                        with open(str(key) + ".over", "w") as f:
                            f.write(res.text)
                        key.unlink(missing_ok=True)
                    else:
                        raise("\n\033[31merror with", res.status_code, "\033[0m")
            except Exception as e:
                print("\n\033[31mPort scan error")
                print(e)
                print("\033[0m")

    time.sleep(10)