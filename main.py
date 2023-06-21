from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

import uuid
import logging


import datetime

import os
from pathlib import Path
if not os.environ.get("LOG_PATH") or not os.environ.get("SCREENSHOT_SAVE_PATH"):
    from dotenv import load_dotenv
    load_dotenv()
SCREENSHOT_SAVE_PATH = os.environ.get("SCREENSHOT_SAVE_PATH")
LOG_PATH = os.environ.get("LOG_PATH")
os.makedirs(SCREENSHOT_SAVE_PATH, exist_ok=True)
os.makedirs(LOG_PATH, exist_ok=True)

logger = logging.getLogger("portscanner")
logger.setLevel("INFO")

now = datetime.datetime.now().strftime("%Y-%m-%d.%H-%M-%S-%f")
fh = logging.FileHandler(f"{LOG_PATH}/{now}.log")
fmt = logging.Formatter("%(asctime)s %(levelname)s\t%(message)s")
fh.setFormatter(fmt)

logger.addHandler(fh)


import portscanner
import url2img

app = FastAPI()


class ScanJob():
    ip: str = ""
    job_uuid = ""
    is_done: bool = False
    result: list = []

    def __init__(self, ip, job_uuid):
        self.ip = ip
        self.job_uuid = job_uuid

    def __call__(self):
        jobs[self.job_uuid] = self
        open_ports = portscanner.scan_ports(self.ip)

        img_uuids = [uuid.uuid4() for _ in range(len(open_ports))]
        captures = url2img.url2img(
                [f"{self.ip}:{p['@portid']}" for p in open_ports], img_uuids
            )
        has_capture = {
            k: v.result() for k, v in captures.items()
        }

        for i, img_uuid in enumerate(img_uuids):
            if has_capture[img_uuid]:
                open_ports[i][
                    "screenshot_uuid"
                ] = img_uuid

        logger.info(
            f"[main:scan_ports] completed a scan request to {self.ip}"
        )

        self.result = open_ports
        self.is_done = True

    def get_result(self):
        del jobs[self.job_uuid]
        return self.result
jobs = {}

class PortDict(BaseModel):
    tcp: list
    udp: list

@app.get("/register")
def register(request: Request, ip: str, background_tasks: BackgroundTasks):
    logger.info(
        f"[main:register] Received a scan request from {request.client.host} to {ip}"
    )
    job_uuid = str(uuid.uuid4())
    sj = ScanJob(ip, job_uuid)
    background_tasks.add_task(sj)

    return {"job_uuid" : job_uuid}

@app.get("/get_result")
def get_result(request: Request, job_uuid: str):
    sj = jobs.get(job_uuid)
    if sj:
        if sj.is_done:
            logger.info(
                f"[main:get_result] Received a scan result query of {job_uuid} from {request.client.host}"
            )
            return sj.get_result()
        else:
            return Response(f'{job_uuid} is now processing', status_code=202)
    else:
        return Response(f'{job_uuid} was not found', status_code=404)



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
        logger.info(
            f"[main:scan_ports] Received a scan request from {request.client.host} to {ip}:{(str(dict(ports))) if ports else ''}"
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

        logger.info(
            f"[main:scan_ports] completed a scan request from {request.client.host} to {ip}:{':' + str(ports) if ports else ''}"
        )
        return open_ports
    except Exception as e:
        logger.error(f"[main:scan_ports] {e}")
        return []


@app.get("/getimg")
def getimg(request: Request, img_uuid: str):
    logger.info(f"[main:getimg] Received a getimg request from {request.client.host} to {img_uuid}")
    save_folder = Path(SCREENSHOT_SAVE_PATH)
    img_path = save_folder / f"{img_uuid}.png"
    if not img_path.exists():
        logger.warning(f"[main:getimg] {img_uuid}.png was not found")
        return None
    if img_path.parent != save_folder:
        logger.warning(f"[main:getimg] {img_uuid}.png's parent folder didn't match.")
        return None

    
    response = FileResponse(img_path, filename=f"{img_uuid}.png")
    logger.info(f"[main:getimg] Send {img_uuid}.png")
    return response

