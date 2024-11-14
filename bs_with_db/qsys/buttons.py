from config import *
from relay import set_all_relay, set_relay, barix_set_relays, barix_set_relay, barix_set_relay_all
from qsys.qsys import qrc
from qsys.qrc_comm import *
from modules.db import Database
from mojo import context

qrc_on_air_timeline = None
qrc_offair_timeline = None

def qrc_stop_offair_relays(_):
    try:
        set_all_relay(False)
        barix_set_relay_all(False)
    except Exception as e:
        print(f"qrc_stop_offair_relays() Exception {e=}")

# qrc onair timeline evt
def _qrc_on_air(_):
    global page, qrc_zones
    try:
        qrc_set_start_onair(qrc, [i + 1 for i, zone_enabled in enumerate(qrc_zones) if zone_enabled])
        qrc_offair_timeline = context.services.get("timeline")
        qrc_offair_timeline.expired.listen(qrc_stop_offair_relays)
        qrc_offair_timeline.start([(page["qrc_max_page_time"] + 5) * 1000], False, 0)
    except Exception as e:
        print(f"_qrc_on_air() Exception {e=}")

def btn_evt_on_air():
    global qrc_on_air_timeline, page
    if page["qrc_onair"]:
        return
    if qrc_on_air_timeline is not None:
        try:
            qrc_on_air_timeline.stop()
            qrc_offair_timeline.stop()
            qrc_on_air_timeline = None
            qrc_offair_timeline = None
        except Exception as e:
            print(f"btn_evt_on_air() Exception {e=}")
            
    try:
        on_air_zones = [i + 1 for i, zone_enabled in enumerate(qrc_zones) if zone_enabled]
        if not on_air_zones:
            DV_TP.port[2].send_command("^PPN-popup_nozone")
            return
        #relay on
        barix_set_relays(on_air_zones, True)
        for idx in on_air_zones:
            set_relay(idx, True)
        # on air timeline start
        qrc_on_air_timeline = context.services.get("timeline")
        qrc_on_air_timeline.expired.listen(_qrc_on_air)
        qrc_on_air_timeline.start([page["power_on_delay"] * 1000], False, 0)
        # onair popup
        DV_TP.port[2].send_command("^PPN-popup_onair")
    except Exception as e:
        print(f"qrc_on_air() Exception {e=}")


def btn_evt_off_air():
    global page
    try:
        if page["qrc_page_id"]:
            qrc_set_stop_on_air(qrc)
        zone_idx_list = [i + 1 for i, zone_enabled in enumerate(qrc_zones) if zone_enabled]
        barix_set_relays(zone_idx_list, False)
        for idx in zone_idx_list:
            set_relay(idx, False)
        page["qrc_onair"] = False
        DV_TP.port[2].send_command("^PPN-popup_offair")
    except Exception as e:
        print(f"qrc_off_air() Exception {e=}")

def _btn_event(btn):
    db = Database()
    global page, barixes_ip_addr, num_of_relays, qrc_zones, qrc_zones_mute
    try:
        if btn.value == False:
            return
        # chime
        btnId = int(btn.id)
        if btnId == 7:
            chime = not db.find_one("setup", {"key": "chime"})["Bool"]
            db.update("setup", {"Bool": chime}, {"key": "chime"})
            DV_TP.port[2].channel[7].value = chime
        # page time
        elif btnId == 3:
            pageTime = min(300, db.find_one("setup", {"key": "pageTime"})["Value"] + 10)
            DV_TP.port[2].send_command(f"^TXT-5,0,{pageTime}s")
            db.update("setup", {"Value": pageTime}, {"key": "pageTime"})
        elif btnId == 4:
            pageTime = max(10, db.find_one("setup", {"key": "pageTime"})["Value"] - 10)
            DV_TP.port[2].send_command(f"^TXT-5,0,{page['qrc_max_page_time']}s")
            db.update("setup", {"Value": pageTime}, {"key": "pageTime"})
        # relay all off
        elif btnId == 10:
            for key, value in barixes_ip_addr.items():
                barix_set_relay(value, False)
            for idx in range(num_of_relays):
                set_relay(idx, False)
        elif btnId == 11:
            btn_evt_on_air()
        elif btnId == 12:
            btn_evt_off_air()
        elif 21 <= btnId <= 44:
            idx = btnId % 20
            sel = db.find_one("zones", {"id": idx})["sel"]
            db.update("zones", {"Sel": not sel}, {"id": idx})
            DV_TP.port[2].channel[idx + 20].value = not sel
        elif btnId >= 101 and btnId <= 124:
            idx = btnId % 100
            qrc_zones_mute[idx - 1] = not qrc_zones_mute[idx - 1]
            qrc_set_zone_mute(qrc, idx, qrc_zones_mute[idx - 1])
            qrc_get_zone_mute(qrc, idx)
        elif btnId >= 201 and btnId <= 224 or btnId >= 301 and btnId <= 324:
            idx = btnId % 100
            gain_change = 1.0 if btnId < 300 else -1.0
            gain = float(qrc_zones_gain[idx - 1]) + gain_change
            qrc_set_zone_gain(qrc, idx, gain)
            qrc_get_zone_gain(qrc, idx)
            
            
    except Exception as e:
        print(f"btn_event() Exception {e=}")

def init_buttons_evt():
    try:
        print("init_buttons_evt()")
        for (i) in range(1, 324):
            if DV_TP.port[2].button[i] is not None:
                DV_TP.port[2].button[i].watch(_btn_event)
    except Exception as e:
        print(f"init_buttons_evt() Exception {e=}")
        
def _swich_menu(btn):
    DV_TP = context.devices.get("AMX-10001")
    try:
        if btn.value == False:
            return
        if int(btn.id) == 100:
            DV_TP.port[1].send_command("^PPX")
            print("close all popoup")
            for idx in range(11, 15):
                DV_TP.port[1].channel[idx].value = False
            return
        else:
            menu_id = int(btn.id) % 10
            page["selected_menu"] = "{0:0>3d}".format(menu_id)
            DV_TP.port[1].send_command(f"^PPN-{page['selected_menu']}")
            for idx in range(11, 15):
                if idx == int(btn.id):
                    DV_TP.port[1].channel[idx].value = True
                else:
                    DV_TP.port[1].channel[idx].value = False
    except Exception as e:
        print(f"_swich_menu() Exception {e=}")
        
def init_UI():
    try:
        for idx in range(11, 15):
            DV_TP.port[1].button[idx].watch(_swich_menu)
            DV_TP.port[1].channel[idx].value = False
        DV_TP.port[1].button[100].watch(_swich_menu)
    except Exception as e:
        print(f"init_UI() Exception {e=}")
        
def update_tp_gain_mute():
    global qrc_zones_gain, qrc_zones_mute, page
    try:
        for idx in range(1, page["num_of_zones"] + 1):
            DV_TP.port[2].channel[idx + 100].value = qrc_zones_mute[idx - 1]
            DV_TP.port[2].send_command(f"^TXT-{idx + 100},0,{str(qrc_zones_gain[idx - 1])}dB")
    except Exception as e:
        print(f"update_tp_gain_mute() Exception {e=}")
        
def update_tp_btn_names():
    global venue_name, zone_name, page
    DV_TP = context.devices.get("AMX-10001")
    try:
        if venue_name:
            DV_TP.port[2].send_command(f"^UNI-{1},0," + "".join(format(ord(char), '04X') for char in venue_name))
        if zone_name and len(zone_name) > 0:
            for zone_id, zone_name in enumerate(zone_name):
                DV_TP.port[2].send_command(f"^UNI-{zone_id + 21},0," + "".join(format(ord(char), '04X') for char in zone_name))
        # update etc
        DV_TP.port[2].channel[7].value = page["qrc_chime"]
        DV_TP.port[2].send_command("^TXT-5,0," + str(page["qrc_max_page_time"]) + "s")
    except Exception as e:
        print(f"update_tp_btn_names() Exception {e=}")
        
def update_ui_from_db():
    db = Database()
    zones = db.fetch("zones")
    for zone in zones:
        if zone["Mute"] is not None and zone["Mute"] == 1:
            DV_TP.port[2].channel[zone['id'] + 100].value = True
        else:
            DV_TP.port[2].channel[zone['id'] + 100].value = False
        if zone["Gain"] is not None:
            DV_TP.port[2].send_command(f"^TXT-{zone['id'] + 100},0,{str(zone['Gain'])}dB")
        if zone["Name"] is not None:
            DV_TP.port[2].send_command(f"^UNI-{zone['id'] + 20},0," + "".join(format(ord(char), '04X') for char in zone['Name']))
            