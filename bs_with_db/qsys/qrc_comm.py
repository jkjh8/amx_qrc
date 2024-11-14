from config import *

def qrc_get_zone_gain(qrc, idx):
    qrc.send(f"gainmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain"}]})

def qrc_get_all_zone_gain(qrc):
    qrc.send("gainmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain"} for idx in range(1, page["num_of_zones"] + 1)]})

def qrc_set_zone_gain(qrc, idx, db):
    qrc.send(f"gainmute", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain", "Value": str(db)}]})

def qrc_get_zone_mute(qrc, idx):
    qrc.send(f"gainmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute"}]})

def qrc_get_all_zone_mute(qrc, ):
    qrc.send("gainmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute"} for idx in range(1, page["num_of_zones"] + 1)]})

def qrc_set_zone_mute(qrc, idx, mute):
    qrc.send(f"gainmute", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute", "Value": mute}]})

def qrc_set_start_onair(qrc, zones):
    qrc.send(
        "page-submit",
        "PA.PageSubmit",
        {
            "Mode": "live",
            "Zones": zones,
            "Priority": 3,
            "Station": 2,
            "Start": True,
            "Preamble": "Chime ascending triple.wav" if page["qrc_chime"] else "",
            "MaxPageTime": int(page["qrc_max_page_time"]),
        },
    )
    page["qrc_onair"] = True
    
def qrc_set_stop_on_air(qrc):
    qrc.send("page-stop", "PA.PageStop", {"PageID": int(page["qrc_page_id"])})
