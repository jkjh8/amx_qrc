from db.db_zones import db_zones_find
from db.db_setup import db_setup_find_one, db_setup_update

def qrc_get_zone_gain(qrc, idx):
    qrc.send(f"getgain", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain"}]})

def qrc_get_zone_mute(qrc, idx):
    qrc.send(f"getmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute"}]})

def qrc_set_zone_gain(qrc, idx, db):
    qrc.send(f"setgain", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain", "Value": str(db)}]})
    
def qrc_set_zone_mute(qrc, idx, mute):
    qrc.send(f"setmute", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute", "Value": mute}]})

def qrc_get_all_zone_gain(qrc):
    qrc.send("getallmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{zone['id']}.gain"} for zone in db_zones_find()]})

def qrc_get_all_zone_mute(qrc):
    qrc.send("getallmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{zone['id']}.mute"} for zone in db_zones_find()]})

def qrc_set_start_onair(qrc, zones):
    chime = db_setup_find_one({"key": "chime"})["Bool"]
    page_time = db_setup_find_one({"key": "pageTime"})["Value"]
    qrc.send(
        "page-submit",
        "PA.PageSubmit",
        {
            "Mode": "live",
            "Zones": zones,
            "Priority": 3,
            "Station": 2,
            "Start": True,
            "Preamble": "Chime ascending triple.wav" if chime else "",
            "MaxPageTime": page_time,
        },
    )
    db_setup_update({"Bool": True}, {"key": "onair"})

def qrc_set_stop_on_air(qrc, pageId):
    qrc.send("page-stop", "PA.PageStop", {"PageID": pageId})
