from mojo import context
from bs import barix_set_relays, barix_set_relay_all
from ButtonHandler import ButtonHandler
from config import *
from tp import *
# from lib_tp import *
from relay import set_relay, set_all_relay
from modules.qrc2 import QRC
from qsys.parser import qrc_parser

qrc_check_event_poll = context.services.get("timeline")
tp_btn_refresh_loop = context.services.get("timeline")

qrc = QRC(qsys_ip_addr, qrc_parser)

def init_qsys():
    qrc.connect()
    
    qrc_check_event_poll.expired.listen(qrc_check_zone_props)
    tp_btn_refresh_loop.expired.listen(_btn_refresh_is_on_air_btn)
    qrc_check_event_poll.start([40000], True, -1)
    tp_btn_refresh_loop.start([1000], True, -1)

# ---------------------------------------------------------------------------- #
qrc_on_air_timeline = None

def qrc_toggle_selected_zone_list(btn):
    global page
    if btn.value == True:
        i = int(btn.id) - 20
        if i >= 0 and i <= page["num_of_zones"]:
            page["tp_qrc_on_air_zone_list"][i - 1] = not page["tp_qrc_on_air_zone_list"][i - 1]
            btn_refresh_zone_selected_btn(i)

def qrc_get_on_air_zone_idx_list():
    global page
    on_air_zone_list = [i + 1 for i, zone_enabled in enumerate(page["tp_qrc_on_air_zone_list"]) if zone_enabled]
    return on_air_zone_list
    
def qrc_set_max_page_time(t):
    global page
    page["qrc_max_page_time"] = t

def qrc_count_up_page_time(btn):
    global page
    if btn.value == True:
        page["qrc_max_page_time"] = min(300, page["qrc_max_page_time"] + 10)
        btn_refresh_page_time_count()
        

def qrc_count_down_page_time(btn):
    global page
    if btn.value == True:
        page["qrc_max_page_time"] = max(10, page["qrc_max_page_time"] - 10)
        btn_refresh_page_time_count()

def qrc_stop_on_air():
    global qrc_on_air_timeline
    if qrc_on_air_timeline is not None:
        try:
            qrc_on_air_timeline.stop()
        except Exception as e:
            print(f"qrc_stop_on_air() Exception {e=}")
        finally:
            qrc_on_air_timeline = None


def qrc_start_on_air():
    global qrc_on_air_timeline, page
    qrc_on_air_timeline = context.services.get("timeline")
    qrc_on_air_timeline.expired.listen(_qrc_on_air)
    qrc_on_air_timeline.start([page["power_on_delay"] * 1000], False, 0)


def qrc_on_air():
    global qrc_on_air_timeline, page
    if page["qrc_is_on_air"]:
        return
    try:
        qrc_stop_on_air()
        on_air_zones = qrc_get_on_air_zone_idx_list()
        if not on_air_zones:
            tp_send_command(DV_TP, 2, "^PPN-popup_nozone")
            return
        barix_set_relays(on_air_zones, True)
        for idx in on_air_zones:
            set_relay(idx, True)
        qrc_start_on_air()
        tp_send_command(DV_TP, 2, "^PPN-popup_onair")
    except Exception as e:
        print(f"qrc_on_air() Exception {e=}")


def _qrc_on_air(_):
    global page
    try:
        qrc.send(
            "page-submit",
            "PA.PageSubmit",
            {
                "Mode": "live",
                "Zones": qrc_get_on_air_zone_idx_list(),
                "Priority": 3,
                "Station": 2,
                "Start": True,
                "Preamble": "Chime ascending triple.wav" if page["qrc_chime"] else "",
                "MaxPageTime": page["qrc_max_page_time"],
            },
        )
        page["qrc_is_on_air"] = True
    except Exception as e:
        print(f"_qrc_on_air() Exception {e=}")


# ---------------------------------------------------------------------------- #
def qrc_off_air():
    global page
    print(page["qrc_page_id"])
    try:
        qrc_stop_on_air()
        if page["qrc_page_id"]:
            qrc.send("page-stop", "PA.PageStop", {"PageID": int(page["qrc_page_id"])})
        zone_idx_list = qrc_get_on_air_zone_idx_list()
        barix_set_relays(zone_idx_list, False)
        for idx in zone_idx_list:
            set_relay(idx, False)
        page["qrc_is_on_air"] = False
        tp_send_command(DV_TP, 2, "^PPN-popup_offair")
    except Exception as e:
        print(f"qrc_off_air() Exception {e=}")

def qrc_get_zone_gain(idx):
    qrc.send(f"zone-{idx}-gain", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain"}]})

def qrc_get_all_zone_gain():
    qrc.send("zone-all-gain", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain"} for idx in range(1, page["num_of_zones"] + 1)]})

def qrc_set_zone_gain(idx, db):
    qrc.send(f"zone-{idx}-gain", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain", "Value": str(db)}]})

def qrc_get_zone_mute(idx):
    qrc.send(f"zone-{idx}-mute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute"}]})

def qrc_get_all_zone_mute():
    qrc.send("zone-all-mute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute"} for idx in range(1, page["num_of_zones"] + 1)]})

def qrc_set_zone_mute(idx, mute):
    qrc.send(f"zone-{idx}-mute", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute", "Value": mute}]})

# ---------------------------------------------------------------------------- #

def qrc_check_zone_props(_):
    global page, qrc
    if page["qrc_is_on_air"] or not qrc.connected:
        return
    try:
        qrc_get_all_zone_gain()
        qrc_get_all_zone_mute()
    except Exception as e:
        print(f"qrc_check_zone_props() Exception {e=}")

def _btn_refresh_is_on_air_btn(_):
    btn_refresh_is_on_air_btn()


def btn_evt_on_air(btn):
    global page
    if btn.value == True:
        if page["qrc_is_on_air"]:
            return
        qrc_on_air()


def btn_evt_off_air(btn):
    if btn.value == True:
        qrc_off_air()


# ---------------------------------------------------------------------------- #
def btn_evt_zone_gain_up(btn):
    global page
    if btn.value == True:
        idx = int(btn.id) % 200
        gain = float(page["qrc_zone_gain_status"][idx - 1]) + 1.0
        qrc_set_zone_gain(idx, float(gain))
        qrc_get_zone_gain(idx)

def btn_evt_zone_gain_down(btn):
    global page
    if btn.value == True:
        idx = int(btn.id) % 300
        gain = float(page["qrc_zone_gain_status"][idx - 1]) - 1.0
        qrc_set_zone_gain(idx, float(gain))
        qrc_get_zone_gain(idx)


# ---------------------------------------------------------------------------- #
def btn_evt_toggle_zone_mute(btn):
    global page
    if btn.value == True:
        idx = int(btn.id) % 100
        qrc_set_zone_mute(idx , not page["qrc_zone_mute_status"][idx-1])
        qrc_get_zone_mute(idx)
# ---------------------------------------------------------------------------- #
def btn_refresh_page_time_count():
    global page
    tp_send_command(DV_TP, 2, "^TXT-5,0," + str(page["qrc_max_page_time"]) + "s")

# ---------------------------------------------------------------------------- #
def toggle_chime(btn):
    global page
    if btn.value == True:
        page["qrc_chime"] = not page["qrc_chime"]
        tp_set_button(DV_TP, 2, 7, page["qrc_chime"])

def btn_reset_all_relay(btn):
    if btn.value == True:
        set_all_relay(False)
        barix_set_relay_all(False)


def tp_add_zone_select_btn():
    for idx in range(1, 24):
        tp_add_watcher(DV_TP, 2, idx + 20, qrc_toggle_selected_zone_list)
        tp_add_watcher(DV_TP, 2, idx + 100, btn_evt_toggle_zone_mute)
        tp_add_watcher(DV_TP, 2, idx + 200, btn_evt_zone_gain_up)
        tp_add_watcher(DV_TP, 2, idx + 300, btn_evt_zone_gain_down)

def tp_add_button_events():
    tp_add_watcher(DV_TP, 2, 7, toggle_chime)
    tp_add_watcher(DV_TP, 2, 3, qrc_count_up_page_time)
    tp_add_watcher(DV_TP, 2, 4, qrc_count_down_page_time)
    tp_add_watcher(DV_TP, 2, 10, btn_reset_all_relay)
    tp_add_watcher(DV_TP, 2, 11, btn_evt_on_air)
    tp_add_watcher(DV_TP, 2, 12, btn_evt_off_air)
