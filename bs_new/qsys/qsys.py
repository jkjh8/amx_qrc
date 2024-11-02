from mojo import context
from bs import barix_set_relays
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

def qrc_toggle_selected_zone_list(i):
    global tp_qrc_on_air_zone_list, num_of_zones
    if i >= 0 and i < num_of_zones:
        tp_qrc_on_air_zone_list[i] = not tp_qrc_on_air_zone_list[i]

def qrc_get_on_air_zone_idx_list():
    global tp_qrc_on_air_zone_list
    on_air_zone_list = [i + 1 for i, zone_enabled in enumerate(tp_qrc_on_air_zone_list) if zone_enabled]
    return on_air_zone_list
    
def qrc_set_max_page_time(t):
    global qrc_max_page_time
    qrc_max_page_time = t

def qrc_count_up_page_time():
    global qrc_max_page_time
    qrc_max_page_time = min(300, qrc_max_page_time + 10)

def qrc_count_down_page_time():
    global qrc_max_page_time
    qrc_max_page_time = max(10, qrc_max_page_time - 10)

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
    global qrc_on_air_timeline, power_on_delay
    qrc_on_air_timeline = context.services.get("timeline")
    qrc_on_air_timeline.expired.listen(_qrc_on_air)
    qrc_on_air_timeline.start([power_on_delay * 1000], False, 0)


def qrc_on_air():
    global qrc_on_air_timeline, qrc_page_id, qrc_is_on_air
    if qrc_is_on_air:
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
    global qrc_is_on_air, qrc_max_page_time, power_on_delay, qrc_chime
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
                "Preamble": "Chime ascending triple.wav" if qrc_chime else "",
                "MaxPageTime": qrc_max_page_time,
            },
        )
        qrc_is_on_air = True
    except Exception as e:
        print(f"_qrc_on_air() Exception {e=}")


# ---------------------------------------------------------------------------- #
def qrc_off_air():
    global qrc_is_on_air, qrc_page_id
    try:
        qrc_stop_on_air()
        if qrc_page_id:
            qrc.send("page-stop", "PA.PageStop", {"PageID": qrc_page_id})
        zone_idx_list = qrc_get_on_air_zone_idx_list()
        barix_set_relays(zone_idx_list, False)
        for idx in zone_idx_list:
            set_relay(idx, False)
        qrc_is_on_air = False
        tp_send_command(DV_TP, 2, "^PPN-popup_offair")
    except Exception as e:
        print(f"qrc_off_air() Exception {e=}")

def qrc_get_zone_gain(idx):
    qrc.send(f"zone-{idx}-gain", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain"}]})

def qrc_get_all_zone_gain():
    qrc.send("zone-all-gain", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain"} for idx in range(1, num_of_zones + 1)]})

def qrc_set_zone_gain(idx, db):
    qrc.send(f"zone-{idx}-gain", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.gain", "Value": str(db)}]})

def qrc_get_zone_mute(idx):
    qrc.send(f"zone-{idx}-mute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute"}]})

def qrc_get_all_zone_mute():
    qrc.send("zone-all-mute", "Component.Get", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute"} for idx in range(1, num_of_zones + 1)]})

def qrc_set_zone_mute(idx, mute):
    qrc.send(f"zone-{idx}-mute", "Component.Set", {"Name": "PA", "Controls": [{"Name": f"zone.{idx}.mute", "Value": mute}]})

# ---------------------------------------------------------------------------- #

def qrc_check_zone_props(_):
    global qrc_is_on_air, qrc
    if qrc_is_on_air or not qrc.connected:
        return
    try:
        qrc_get_all_zone_gain()
        qrc_get_all_zone_mute()
    except Exception as e:
        print(f"qrc_check_zone_props() Exception {e=}")

def _btn_refresh_is_on_air_btn(_):
    btn_refresh_is_on_air_btn()


def btn_evt_on_air():
    global qrc_is_on_air
    if qrc_is_on_air:
        return
    qrc_on_air()


def btn_evt_off_air():
    qrc_off_air()


# ---------------------------------------------------------------------------- #
def btn_evt_zone_gain_up(idx):
    global qrc_zone_gain_status
    # idx = int(evt.id) % 100
    gain = float(qrc_zone_gain_status[idx - 1]) + 1.0
    qrc_set_zone_gain(idx, float(gain))
    qrc_get_zone_gain(idx)


def btn_evt_zone_gain_down(idx):
    global qrc_zone_gain_status
    # idx = int(evt.id) % 100
    gain = float(qrc_zone_gain_status[idx - 1]) - 1.0
    qrc_set_zone_gain(idx, float(gain))
    qrc_get_zone_gain(idx)


# ---------------------------------------------------------------------------- #
def btn_evt_toggle_zone_mute(idx):
    global qrc_zone_mute_status
    qrc_set_zone_mute(idx, not qrc_zone_mute_status[idx - 1])
    qrc_get_zone_mute(idx)


# ---------------------------------------------------------------------------- #
def btn_evt_toggle_selected_zone(idx):
    # idx = int(evt.id) % 10
    qrc_toggle_selected_zone_list(idx - 1)
    btn_refresh_zone_selected_btn(idx)
    # print(f"btn_evt_toggle_selected_zone() {tp_qrc_on_air_zone_list}")

# ---------------------------------------------------------------------------- #
def btn_refresh_page_time_count():
    global qrc_max_page_time
    tp_send_command(DV_TP, 2, "^TXT-5,0," + str(qrc_max_page_time) + "s")

# ---------------------------------------------------------------------------- #
def toggle_chime():
    global qrc_chime
    qrc_chime = not qrc_chime
    btn_refresh_chime_btn()

def btn_reset_all_relay():
    print(f"btn_reset_all_relay()")
    set_all_relay(False)


# ---------------------------------------------------------------------------- #
def _tp_add_button_events():
    button_toggle_chime = ButtonHandler()
    button_toggle_chime.add_event_handler("push", toggle_chime)
    tp_add_watcher(DV_TP, 2, 7, button_toggle_chime.handle_event)
    button_page_time_count_up = ButtonHandler()
    button_page_time_count_up.add_event_handler("push", qrc_count_up_page_time)
    button_page_time_count_up.add_event_handler("release", btn_refresh_page_time_count)
    tp_add_watcher(DV_TP, 2, 3, button_page_time_count_up.handle_event)
    button_page_time_count_down = ButtonHandler()
    button_page_time_count_down.add_event_handler("push", qrc_count_down_page_time)
    button_page_time_count_down.add_event_handler("release", btn_refresh_page_time_count)
    tp_add_watcher(DV_TP, 2, 4, button_page_time_count_down.handle_event)
    button_on_air = ButtonHandler()
    button_on_air.add_event_handler("push", btn_evt_on_air)
    tp_add_watcher(DV_TP, 2, 11, button_on_air.handle_event)
    button_off_air = ButtonHandler()
    button_off_air.add_event_handler("push", btn_evt_off_air)
    tp_add_watcher(DV_TP, 2, 12, button_off_air.handle_event)
    button_reset_all_relay = ButtonHandler()
    button_reset_all_relay.add_event_handler("push", btn_reset_all_relay)
    tp_add_watcher(DV_TP, 2, 10, button_reset_all_relay.handle_event)
    # ---------------------------------------------------------------------------- #
    for idx in range(1, num_of_zones + 1):
        button_toggle_zone = ButtonHandler()
        button_toggle_zone.add_event_handler("push", lambda idx=idx: btn_evt_toggle_selected_zone(idx))
        tp_add_watcher(DV_TP, 2, idx + 20, button_toggle_zone.handle_event)
        button_zone_toggle_mute = ButtonHandler()
        button_zone_toggle_mute.add_event_handler("push", lambda idx=idx: btn_evt_toggle_zone_mute(idx))
        tp_add_watcher(DV_TP, 2, idx + 100, button_zone_toggle_mute.handle_event)
        button_zone_gain_up = ButtonHandler(repeat_interval=0.3)
        button_zone_gain_up.add_event_handler("repeat", lambda idx=idx: btn_evt_zone_gain_up(idx))
        tp_add_watcher(DV_TP, 2, idx + 200, button_zone_gain_up.handle_event)
        button_zone_gain_down = ButtonHandler(repeat_interval=0.3)
        button_zone_gain_down.add_event_handler("repeat", lambda idx=idx: btn_evt_zone_gain_down(idx))
        tp_add_watcher(DV_TP, 2, idx + 300, button_zone_gain_down.handle_event)


