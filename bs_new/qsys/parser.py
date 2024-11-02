from config import *
from tp import *

def check_on_air():
    global qrc_is_on_air
    qrc_is_on_air = any(zone is True for zone in qrc_zone_on_air_status)
    return qrc_is_on_air


def qrc_parser(data):
    global qrc_zone_gain_status, qrc_zone_mute_status, qrc_zone_on_air_status, qrc_page_id, qrc_page_status, qrc_is_on_air
    try:
        if "result" in data:
            if data.get("id") == "page-submit" and "PageID" in data["result"]:
                qrc_page_id = data["result"]["PageID"]
            if hasattr(data["result"], "items") and data["result"].get("Name") == "PA":
                update_zone_gain_mute(data["result"]["Controls"])
        elif "method" in data:
            if data.get("method") == "PA.PageStatus":
                if ("params", "PageID") in data.items():
                    qrc_page_status = data["params"]["State"] + "-" +data["params"]["SubState"]
                    print(f"qrc_page_status = {qrc_page_status=}")
            elif data.get("method") == "PA.ZoneStatus":
                if "params" in data.keys():
                    zone = data["params"]["Zone"]
                    active = data["params"]["Active"]
                    qrc_zone_on_air_status[zone - 1] = active
                    qrc_is_on_air = check_on_air()
                    if not qrc_is_on_air:
                        tp_send_command(DV_TP, 2, "^PPF-popup_onair")
                    btn_refresh_is_on_air_btn()
                    btn_refresh_zone_on_air_btn()
        elif "error" in data:
            print(f"qrc_parser recv Error {data=}")
    except Exception as e:
        print(f"qrc_parser() {e=}")
    print(f"qrc_parser() {data=}")
    
    
def update_zone_gain_mute(controls):
    global qrc_zone_gain_status, qrc_zone_mute_status, num_of_zones
    try:
        for control in controls:
            c_name = control["Name"].split(".")
            c_type = c_name[2]
            c_idx = int(c_name[1])
            if c_idx < 1 or c_idx > num_of_zones:
                return
            c_idx -= 1
            if c_type == "gain":
                qrc_zone_gain_status[c_idx] = float(control["Value"])
                tp_update_gain(c_idx)
                
            elif c_type == "mute":
                qrc_zone_mute_status[c_idx] = control["Value"] == 1.0
                tp_set_button(DV_TP, 2, 100+c_idx, qrc_zone_mute_status[c_idx])
                
    except Exception as e:
        print(f"update_zone_gain_mute() {e=}")
    print(f"update_zone_gain_mute() {controls=}")