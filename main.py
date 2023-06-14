from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

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
os.makedirs(SCREENSHOT_SAVE_PATH, exist_ok=True)
os.makedirs(LOG_PATH, exist_ok=True)
logging.basicConfig(filename=f"{LOG_PATH}/{today}.log", level=logging.INFO)

import portscanner
import url2img

app = FastAPI()


class PortDict(BaseModel):
    tcp: list
    udp: list


@app.get("/scan")
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
        img_uuids = [uuid.uuid4() for _ in range(len(open_ports))]
        has_capture = {
            k: v.result()
            for k, v in url2img.url2img(
                [f"{ip}:{p['@portid']}" for p in open_ports], img_uuids
            ).items()
        }

        for i, img_uuid in enumerate(img_uuids):
            if has_capture[img_uuid]:
                open_ports[i][
                    "screenshot_uuid"
                ] = img_uuid

        logging.info(
            f"{datetime.datetime.now()}[main:scan_ports] completed a scan request from {request.client.host} to {ip}:{':' + str(ports) if ports else ''}"
        )
        return open_ports
    except Exception as e:
        logging.error(f"{datetime.datetime.now()}[main:scan_ports] {e}")
        return []


@app.get("/getimg")
def getimg(request: Request, img_uuid: str):
    logging.info(f"{datetime.datetime.now()}[main:getimg] Received a getimg request from {request.client.host} to {img_uuid}")
    img_path = f"{SCREENSHOT_SAVE_PATH}/{img_uuid}.png"
    if not os.path.exists(img_path):
        logging.warning(f"{datetime.datetime.now()}[main:getimg] {img_uuid} was not found")
        return None
    response = FileResponse(img_path, filename=f"{img_uuid}.png")
    logging.info(f"{datetime.datetime.now()}[main:getimg] Send {img_uuid}.png")
    return response

