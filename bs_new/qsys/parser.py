from config import *
from tp import *

def check_on_air():
    global page
    page["qrc_onair"] = any(zone is True for zone in qrc_zones_onair)
    return page["qrc_onair"]

def qrc_parser(data):
    global page
    try:
        if "result" in data:
            if data.get("id") == "page-submit":
                if data["result"]["PageID"]:
                    page["qrc_page_id"] = data["result"]["PageID"]
                    print(f"update qrc_page_id = {page=}")
            if hasattr(data["result"], "items") and data["result"].get("Name") == "PA":
                update_zone_gain_mute(data["result"]["Controls"])
        elif "method" in data:
            if data.get("method") == "PA.PageStatus":
                if ("params", "PageID") in data.items():
                    page["qrc_page_status"] = data["params"]["State"] + "-" +data["params"]["SubState"]
                    logger.info("update qrc_page_status = $s" % page["qrc_page_status"])
            elif data.get("method") == "PA.ZoneStatus":
                if "params" in data.keys():
                    zone = data["params"]["Zone"]
                    active = data["params"]["Active"]
                    qrc_zones_onair[zone - 1] = active
                    page["qrc_onair"] = check_on_air()
                    if not page["qrc_onair"]:
                        tp_send_command(DV_TP, 2, "^PPF-popup_onair")
                    btn_refresh_is_on_air_btn()
                    btn_refresh_zone_on_air_btn()
        elif "error" in data:
            print(f"qrc_parser recv Error {data=}")
    except Exception as e:
        print(f"qrc_parser() {e=}")
    
def update_zone_gain_mute(controls):
    global page
    try:
        for control in controls:
            c_name = control["Name"].split(".")
            c_type = c_name[2]
            c_idx = int(c_name[1])
            if c_idx < 1 or c_idx > page["num_of_zones"]:
                return
            c_idx
            if c_type == "gain":
                qrc_zones_gain[c_idx - 1] = float(control["Value"])
                tp_update_gain(c_idx)
                
            elif c_type == "mute":
                qrc_zones_mute[c_idx - 1] = control["Value"] == 1.0
                tp_set_button(DV_TP, 2, 100 + c_idx, qrc_zones_mute[c_idx -1])
                
    except Exception as e:
        print(f"update_zone_gain_mute() {e=}")