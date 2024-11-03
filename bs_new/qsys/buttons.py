from config import *
from tp import *
from relay import set_all_relay, set_relay, barix_set_relays, barix_set_relay_all
from qsys.qsys import qrc
from qsys.qrc_comm import *

qrc_on_air_timeline = None

def btn_refresh_page_time_count():
    global page
    tp_send_command(DV_TP, 2, "^TXT-5,0," + str(page["qrc_max_page_time"]) + "s")

def qrc_get_on_air_zone_idx_list():
    global page, qrc_zones
    on_air_zone_list = [i + 1 for i, zone_enabled in enumerate(qrc_zones) if zone_enabled]
    return on_air_zone_list

def toggle_chime(btn):
    global page
    try:
        if btn.value == False:
            return
        page["qrc_chime"] = not page["qrc_chime"]
        tp_set_button(DV_TP, 2, 7, page["qrc_chime"])
    except Exception as e:
        print(f"toggle_chime() Exception {e=}")

def qrc_page_time(btn):
    global page
    try:
        if btn.value == False:
            return
        btnId = int(btn.id)
        if btnId == 3:
            page["qrc_max_page_time"] = min(300, page["qrc_max_page_time"] + 10)
        elif btnId == 4:
            page["qrc_max_page_time"] = max(10, page["qrc_max_page_time"] - 10)
        btn_refresh_page_time_count()
    except Exception as e:
        print(f"qrc_page_time() Exception {e=}")
    
def btn_reset_all_relay(btn):
    try:
        if btn.value == False:
            return
        set_all_relay(False)
        barix_set_relay_all(False)
    except Exception as e:
        print(f"btn_reset_all_relay() Exception {e=}")

def qrc_stop_on_air():
    global qrc_on_air_timeline
    if qrc_on_air_timeline is not None:
        try:
            qrc_on_air_timeline.stop()
        except Exception as e:
            print(f"qrc_stop_on_air() Exception {e=}")
        finally:
            qrc_on_air_timeline = None

# qrc onair timeline evt
def _qrc_on_air(_):
    global page
    try:
        qrc_set_start_onair(qrc, qrc_get_on_air_zone_idx_list())
    except Exception as e:
        print(f"_qrc_on_air() Exception {e=}")

def btn_evt_on_air(btn):
    global qrc_on_air_timeline, page
    try:
        if btn.value == False:
            return
        if page["qrc_onair"]:
            return
        qrc_stop_on_air()
        on_air_zones = qrc_get_on_air_zone_idx_list()
        if not on_air_zones:
            tp_send_command(DV_TP, 2, "^PPN-popup_nozone")
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
        tp_send_command(DV_TP, 2, "^PPN-popup_onair")
    except Exception as e:
        print(f"qrc_on_air() Exception {e=}")


def btn_evt_off_air(btn):
    global page
    try:
        if btn.value == True:
            if page["qrc_page_id"]:
                qrc_set_stop_on_air(qrc)
            zone_idx_list = qrc_get_on_air_zone_idx_list()
            barix_set_relays(zone_idx_list, False)
            for idx in zone_idx_list:
                set_relay(idx, False)
            page["qrc_onair"] = False
            tp_send_command(DV_TP, 2, "^PPN-popup_offair")
    except Exception as e:
        print(f"qrc_off_air() Exception {e=}")
        
def qrc_toggle_selected_zone_list(btn):
    global page, qrc_zones
    if btn.value == True:
        i = int(btn.id) - 20
        if i >= 0 and i <= page["num_of_zones"]:
            qrc_zones[i - 1] = not qrc_zones[i - 1]
            tp_set_button(DV_TP, 2, i + 20, qrc_zones[i - 1])
            
def btn_evt_toggle_zone_mute(btn):
    global page, qrc_zones_mute
    try:
        if btn.value == False:
            return
        idx = int(btn.id) % 100
        qrc_set_zone_mute(qrc, idx , not qrc_zones_mute[idx-1])
        qrc_get_zone_mute(qrc, idx)
    except Exception as e:
        print(f"btn_evt_toggle_zone_mute() Exception {e=}")
        
def btn_evt_zone_gain(btn):
    global page, qrc_zones_gain
    try:
        if btn.value == False:
            return
        btnId = int(btn.id)
        idx = btnId % 100
        gain_change = 1.0 if btnId < 300 else -1.0
        gain = float(qrc_zones_gain[idx - 1]) + gain_change
        qrc_set_zone_gain(qrc, idx, gain)
        qrc_get_zone_gain(qrc, idx)
    except Exception as e:
        print(f"btn_evt_zone_gain() Exception {e=}")

def init_buttons_evt():
    try:
        tp_add_watcher(DV_TP, 2, 7, toggle_chime)
        tp_add_watcher(DV_TP, 2, 3, qrc_page_time)
        tp_add_watcher(DV_TP, 2, 4, qrc_page_time)
        tp_add_watcher(DV_TP, 2, 10, btn_reset_all_relay)
        tp_add_watcher(DV_TP, 2, 11, btn_evt_on_air)
        tp_add_watcher(DV_TP, 2, 12, btn_evt_off_air)
        for idx in range(1, 24):
            tp_add_watcher(DV_TP, 2, idx + 20, qrc_toggle_selected_zone_list)
            tp_add_watcher(DV_TP, 2, idx + 100, btn_evt_toggle_zone_mute)
            tp_add_watcher(DV_TP, 2, idx + 200, btn_evt_zone_gain)
            tp_add_watcher(DV_TP, 2, idx + 300, btn_evt_zone_gain)
    except Exception as e:
        print(f"init_buttons_evt() Exception {e=}")
        