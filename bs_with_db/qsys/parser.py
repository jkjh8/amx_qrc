from config import *
import re
from db.db_setup import db_setup_find_one, db_setup_update
from db.db_zones import db_zones_find, db_zones_find_one, db_zones_update, db_zones_exists
DV_TP = context.devices.get("AMX-10001")

def qrc_parser(data):
    try:
        if "result" in data:
            if "id" in data and data.get("id") == "page-submit":
                if data["result"]["PageID"]:
                    return db_setup_update({"Value": data["result"]["PageID"]}, {"key": "pageId"})
            elif "id" in data and data.get("id") in ["getmute", "getgain", "getAllmute", "getAllgain"]:
                return update_zone_gain_mute(data["result"]["Controls"])
        elif "method" in data:
            if data.get("method") == "PA.PageStatus":
                if ("params", "PageID") in data.items():
                    pageMessage = data["params"]["State"] + "-" + data["params"]["SubState"]
                    db_setup_update({"String": pageMessage}, {"key": "pageStatus"})
                    return logger.info("update qrc_page_status = $s" % pageMessage)
            elif data.get("method") == "PA.ZoneStatus":
                if "params" in data.keys():
                    db_zones_update({"Active": data["params"]["Active"]}, {"id": data["params"]["Zone"]}, True)
                    on_air = db_zones_exists({"Active": True})
                    if on_air == 0:
                        db_setup_update({"Bool": False}, {"key":"onair"})
                        DV_TP.port[2].send_command("^PPF-popup_onair")
                    else:
                        db_setup_update({"Bool": True}, {"key":"onair"})
                    # # onair btn
                    DV_TP.port[2].channel[11].value = on_air == 0
                    DV_TP.port[2].channel[12].value = not on_air== 0
                    # zones
                    zones = db_zones_find()
                    for zone in zones:
                        DV_TP.port[2].channel[int(zone["id"]) + 50].value = zone["Active"]

        elif "error" in data:
            print(f"qrc_parser recv Error {data=}")
    except Exception as e:
        print(f"qrc_parser() {e=}")
    
def update_zone_gain_mute(controls):
    try:
        for control in controls:
            c_idx = int(re.search(r'\d+', control["Name"]).group())
            if re.search(r'gain', control["Name"]):
                db_zones_update({"Gain": control["Value"]}, {"id": c_idx}, True)
                DV_TP.port[2].send_command("^TXT-" + str(100 + c_idx) + ",0," + str(control["Value"]) + 'dB')
            elif re.search(r'mute', control["Name"]):
                db_zones_update({"Mute": control["Value"] == 1.0}, {"id": c_idx}, True)
                DV_TP.port[2].channel[100 + c_idx].value = control["Value"] == 1.0
            else:
                return
    except Exception as e:
        print(f"update_zone_gain_mute() {e=}")