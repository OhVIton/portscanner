import subprocess
from tempfile import NamedTemporaryFile
import xmltodict

import logging

import os
from dotenv import load_dotenv

import logging

load_dotenv()
SCREENSHOT_SAVE_PATH = os.environ.get("SCREENSHOT_SAVE_PATH")
LOG_PATH = os.environ.get("LOG_PATH")

logger = logging.getLogger("portscanner")



def scan_ports(
    ip: str,
    ports={
        "tcp": [
            "21",
            "22",
            "80",
            "81",
            "443",
            "445",
            "1723",
            "3389",
            "5431",
            "8000",
            "8080",
            "49152",
            "52869",
        ],
        "udp": [
            "19",
            "53",
            "123",
            "500",
            "1701",
            "1900",
            "5000",
            "5350",
            "5351",
            "5353",
            "11211",
        ],
    },
):
    try:
        logger.info(f"[portscanner] start a portscan to {ip}")
        logger.debug(
            f"[portscanner] Scan will be held at {ports}"
        )
        sr = _nmap([ip], ports)
        # openなポートのみ取り出す
        sr_ports = [
            p
            for p in sr["nmaprun"]["host"]["ports"]["port"]
            if p["state"]["@state"] == "open"
        ]

        logger.info(
            f"[portscanner] {ip} has open ports {str(sr_ports)}"
        )

        return sr_ports

    except KeyError as ke:
        logger.info(
            f"[portscanner] {ip} has no open ports available"
        )
        return []


def _portargs(portdict: dict):
    outlist = []
    for protocol, ports in portdict.items():
        if protocol == "tcp":
            h = "T:"
        elif protocol == "udp":
            h = "U:"
        else:
            raise Exception(protocol + "is not tcp nor udp.")

        outlist += [f"{h}{port}" for port in ports]
    return ",".join(outlist)


def _nmap(iplist, portdict) -> dict:
    with NamedTemporaryFile(mode="w+t") as ipf, NamedTemporaryFile(mode="w+t") as xmlf:
        for ip in iplist:
            ipf.write(ip + "\n")

        ipf.flush()

        subprocess.run(
            ["nmap", "-p", _portargs(portdict), "-i", ipf.name, "-oX", xmlf.name],
            capture_output=True,
            text=True,
        )

        srdict = xmltodict.parse(xmlf.read())
    return srdict
