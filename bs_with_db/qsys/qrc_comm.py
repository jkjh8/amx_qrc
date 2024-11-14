from modules.db import Database


def qrc_get_zone_gain(qrc, idx):
    qrc.send(f"gainmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain"}]})

def qrc_get_all_zone_gain(qrc):
    db = Database()
    zones = db.fetch("zones")
    qrc.send("gainmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{zone['id']}.gain"} for zone in zones]})

def qrc_set_zone_gain(qrc, idx, db):
    qrc.send(f"gainmute", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain", "Value": str(db)}]})

def qrc_get_zone_mute(qrc, idx):
    qrc.send(f"gainmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute"}]})

def qrc_get_all_zone_mute(qrc):
    db = Database()
    zones = db.fetch("zones")
    qrc.send("gainmute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{zone['id']}.mute"} for zone in zones]})

def qrc_set_zone_mute(qrc, idx, mute):
    qrc.send(f"gainmute", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute", "Value": mute}]})

def qrc_set_start_onair(qrc, zones):
    db = Database()
    chime = db.find_one("setup", {"key": "chime"}).get("Bool", False)
    page_time = db.find_one("setup", {"key": "pageTime"}).get("Value", 30)
    
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
    page["qrc_onair"] = True
    
def qrc_set_stop_on_air(qrc):
    db = Database()
    qrc.send("page-stop", "PA.PageStop", {"PageID": db.find_one("setup", {"key": "pageId"}).get("Value", 0)})
