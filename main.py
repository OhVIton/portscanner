from fastapi import FastAPI, Request
from pydantic import BaseModel
import portscanner
import url2img

import uuid
import logging

import datetime

from concurrent.futures import ThreadPoolExecutor

import os
from dotenv import load_dotenv

load_dotenv()
today = datetime.date.today()
SCREENSHOT_SAVE_PATH = os.environ.get("SCREENSHOT_SAVE_PATH")
LOG_PATH = os.environ.get("LOG_PATH")
logging.basicConfig(filename=f"{LOG_PATH}/{today}.log", level=logging.INFO)

app = FastAPI()


class PortDict(BaseModel):
    tcp: list
    udp: list


@app.post("/scan")
def scan_ports(request: Request, ip: str, ports: PortDict = None):
    """
    ports:

    {
        "tcp":
            ["22", "23", "80", ...],
        ,
        "udp":
            ["22", "24", "26", ...]
    }
    """
    try:
        logging.info(
            f"{datetime.datetime.now()}[main:scan_ports] Received a scan request from {request.client.host} to {ip}:{(str(dict(ports))) if ports else ''}"
        )
        if ports:
            open_ports = portscanner.scan_ports(ip, dict(ports))
        else:
            open_ports = portscanner.scan_ports(ip)

        """
        for idx, port in enumerate(open_ports):
            img_uuid = uuid.uuid4()
            if url2img.url2img(
                f"{ip}:{port['@portid']}", f"{SCREENSHOT_SAVE_PATH}/{img_uuid}.png"
            ):
                open_ports[idx]["screenshot_path"] = img_uuid
        """
        img_fnames = [uuid.uuid4() for _ in range(len(open_ports))]
        has_capture = {
            k: v.result()
            for k, v in url2img.url2img(
                [f"{ip}:{p['@portid']}" for p in open_ports], img_fnames
            ).items()
        }

        for i, img_fname in enumerate(img_fnames):
            if has_capture[img_fname]:
                open_ports[i][
                    "screenshot_path"
                ] = f"{SCREENSHOT_SAVE_PATH}/{img_fname}.png"

        logging.info(
            f"{datetime.datetime.now()}[main:scan_ports] completed a scan request from {request.client.host} to {ip}:{':' + str(ports) if ports else ''}"
        )
        return open_ports
    except Exception as e:
        logging.error(f"{datetime.datetime.now()}[main:scan_ports] {e}")
        return []
