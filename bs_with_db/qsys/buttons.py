from relay import set_all_relay, set_relay, barix_set_relays, barix_set_relay, barix_set_relay_all
from qsys.qrc_comm import *
from db.db_setup import db_setup_find, db_setup_find_one, db_setup_update
from db.db_zones import db_zones_find, db_zones_find_one, db_zones_update
from mojo import context

DV_TP = context.devices.get("AMX-10001")
qrc_on_air_timeline = None
qrc_offair_timeline = None

def qrc_stop_offair_relays(_):
    try:
        print("qrc_stop_offair_relays()")
        # DV_TP.port[2].send_command("^PPN-popup_offair")
        set_all_relay(False)
        barix_set_relay_all(False)
    except Exception as e:
        print(f"qrc_stop_offair_relays() Exception {e=}")

# qrc onair timeline evt
def _qrc_on_air(_):
    global qrc_offair_timeline
    try:
        from index import qrc
        qrc_set_start_onair(qrc, [zone["id"] for zone in db_zones_find({"Sel": True})])
        qrc_offair_timeline = context.services.get("timeline")
        qrc_offair_timeline.expired.listen(qrc_stop_offair_relays)
        qrc_offair_timeline.start([(db_setup_find_one({"key":"pageTime"})["Value"] + 5) * 1000], False, 0)
    except Exception as e:
        print(f"_qrc_on_air() Exception {e=}")

def btn_evt_on_air():
    global qrc_on_air_timeline, qrc_offair_timeline
    if db_setup_find_one({"key":"onair"})["Bool"]:
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
        selected = [zone["id"] for zone in db_zones_find({"Sel": True})]
        if not selected:
            DV_TP.port[2].send_command("^PPN-popup_nozone")
            return
        #relay on
        barix_set_relays(selected, True)
        for idx in selected:
            set_relay(idx, True)
        # on air timeline start
        qrc_on_air_timeline = context.services.get("timeline")
        qrc_on_air_timeline.expired.listen(_qrc_on_air)
        qrc_on_air_timeline.start([db_setup_find_one({"key":"powerOnDelay"})["Value"] * 1000], False, 0)
        # onair popup
        DV_TP.port[2].send_command("^PPN-popup_onair")
    except Exception as e:
        print(f"qrc_on_air() Exception {e=}")


def btn_evt_off_air():
    from qsys.qsys import qrc
    try:
        pageId = db_setup_find_one({"key": "pageId"})["Value"]
        if pageId:
            qrc_set_stop_on_air(qrc, pageId)
        selected = [zone["id"] for zone in db_zones_find({"Sel": True})]
        barix_set_relays(selected, False)
        for idx in selected:
            set_relay(idx, False)
        db_setup_update({"Bool": False}, {"key": "onair"})
        DV_TP.port[2].send_command("^PPF-popup_onair")
    except Exception as e:
        print(f"qrc_off_air() Exception {e=}")

def _btn_event(btn):
    try:
        from index import qrc
        if btn.value == False:
            return
        # chime
        btnId = int(btn.id)
        if btnId == 7:
            chime = not db_setup_find_one({"key": "chime"})["Bool"]
            db_setup_update({"Bool": chime}, {"key": "chime"})
            DV_TP.port[2].channel[7].value = chime
        # page time
        elif btnId == 3:
            pageTime = min(300, db_setup_find_one({"key":"pageTime"})["Value"] + 10)
            db_setup_update({"Value": pageTime}, {"key": "pageTime"})
            DV_TP.port[2].send_command(f"^TXT-5,0,{pageTime}s")
        elif btnId == 4:
            pageTime = max(10, db_setup_find_one({"key":"pageTime"})["Value"] - 10)
            db_setup_update({"Value": pageTime}, {"key": "pageTime"})
            DV_TP.port[2].send_command(f"^TXT-5,0,{pageTime}s")
        # relay all off
        elif btnId == 10:
            barix_set_relay_all(False)
            set_all_relay(False)
        elif btnId == 11:
            btn_evt_on_air()
        elif btnId == 12:
            btn_evt_off_air()
        elif 21 <= btnId <= 44:
            idx = btnId % 20
            sel = db_zones_find_one({"id": idx})["Sel"]
            db_zones_update({"Sel": not sel}, {"id": idx})
            DV_TP.port[2].channel[idx + 20].value = not sel
        elif btnId >= 101 and btnId <= 124:
            idx = btnId % 100
            mute = not db_zones_find_one({"id": idx})["Mute"]
            qrc_set_zone_mute(qrc, idx, mute)
            qrc_get_zone_mute(qrc, idx)
        elif btnId >= 201 and btnId <= 224 or btnId >= 301 and btnId <= 324:
            idx = btnId % 100
            gain_change = 1.0 if btnId < 300 else -1.0
            gain = db_zones_find_one({"id": idx})["Gain"]
            gain = float(gain) + gain_change
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
    try:
        if btn.value == False:
            return
        btnId = int(btn.id) % 10
        if int(btn.id) == 100:
            DV_TP.port[1].send_command("^PPX")
            for idx in range(11, 15):
                DV_TP.port[1].channel[idx].value = False
            return
        else:
            DV_TP.port[1].send_command(f"^PPN-{btnId:03d}")
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
        
def update_ui_from_db():
    try:
        setup = db_setup_find()
        zones = db_zones_find()
        for item in setup:
            if item["key"] == "chime":
                DV_TP.port[2].channel[7].value = item["Bool"]
            if item["key"] == "pageTime":
                DV_TP.port[2].send_command(f"^TXT-5,0,{item['Value']}s")
        for zone in zones:
            if zone["Mute"] is not None and zone["Mute"] == 1:
                DV_TP.port[2].channel[zone['id'] + 100].value = True
            else:
                DV_TP.port[2].channel[zone['id'] + 100].value = False
            if zone["Gain"] is not None:
                DV_TP.port[2].send_command(f"^TXT-{zone['id'] + 100},0,{str(zone['Gain'])}dB")
            if zone["Name"] is not None:
                DV_TP.port[2].send_command(f"^UNI-{zone['id'] + 20},0," + "".join(format(ord(char), '04X') for char in zone['Name']))                
    except Exception as e:
        print(f"update ui from db Error {e}")