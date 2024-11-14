from config import *
import re
from modules.db import Database

def qrc_parser(data):
    print(data)
    db = Database()
    try:
        if "result" in data and data.get("id") == "page-submit":
            if data["result"]["PageID"]:
                db.update("setup", {"Value": data["result"]["PageID"]}, {"key": "pageId"}, upsert=True)
                return
        if "result" in data and data.get("id") == "gainmute" and "Controls" in data["result"]:
            update_zone_gain_mute(data["result"]["Controls"])
            return
        if "method" in data:
            if data.get("method") == "PA.PageStatus":
                if ("params", "PageID") in data.items():
                    pageMessage = data["params"]["State"] + "-" + data["params"]["SubState"]
                    db.update("setup", {"String": pageMessage}, {"key": "pageStatus"}, upsert=True)
                    logger.info("update qrc_page_status = $s" % pageMessage)
                    return
            elif data.get("method") == "PA.ZoneStatus":
                if "params" in data.keys():
                    zone = data["params"]["Zone"]
                    active = data["params"]["Active"]
                    db.update("zones", {"Active": active == True}, {"id": zone}, upsert=True)
                    r = db.find("zones", {"Active": True})
                    onair = 0 < len(r)
                    if not onair:
                        DV_TP.port[2].send_commnad("^PPF-popup_onair")
                    # onair btn
                    DV_TP.port[2].channel[11].value = onair
                    DV_TP.port[2].channel[12].value = not onair
                    # zones
                    zones = db.fetch("zones")
                    for zone in zones:
                        DV_TP.port[2].channel[zone["id"] + 50].value = zone["Active"]

        if "error" in data:
            print(f"qrc_parser recv Error {data=}")
    except Exception as e:
        print(f"qrc_parser() {e=}")
    
def update_zone_gain_mute(controls):
    global page
    db = Database()
    try:
        for control in controls:
            if re.search(r'gain', control["Name"]):
                c_type = "gain"
            elif re.search(r'mute', control["Name"]):
                c_type = "mute"
            else:
                return
            c_idx = int(re.sub(r'[^0-9]','', control["Name"]))
            if c_type == "gain":
                db.update("zones", {"Gain": control["Value"]}, {"id": c_idx}, upsert=True)
                DV_TP.port[2].send_command("^TXT-" + str(100 + c_idx) + ",0," + str(control["Value"]) + 'dB')
            elif c_type == "mute":
                db.update("zones", {"Mute": control["Value"] == 1.0}, {"id": c_idx}, upsert=True)
                DV_TP.port[2].channel[100 + c_idx].value = control["Value"] == 1.0
                
    except Exception as e:
        print(f"update_zone_gain_mute() {e=}")