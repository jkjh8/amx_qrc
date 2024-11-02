from config import *
from tp import *
from bs import barix_set_relay_all, barix_set_relays
from relay import set_all_relay, set_relay
from qsys.qsys import qrc

qrc_on_air_timeline = None

def btn_refresh_page_time_count():
    global page
    tp_send_command(DV_TP, 2, "^TXT-5,0," + str(page["qrc_max_page_time"]) + "s")

def qrc_get_on_air_zone_idx_list():
    global page
    on_air_zone_list = [i + 1 for i, zone_enabled in enumerate(page["tp_qrc_on_air_zone_list"]) if zone_enabled]
    return on_air_zone_list

def toggle_chime(btn):
    global page
    if btn.value == True:
        page["qrc_chime"] = not page["qrc_chime"]
        tp_set_button(DV_TP, 2, 7, page["qrc_chime"])
        
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

def btn_reset_all_relay(btn):
    if btn.value == True:
        set_all_relay(False)
        barix_set_relay_all(False)
        
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


def btn_evt_on_air(btn):
    global page
    if btn.value == True:
        if page["qrc_is_on_air"]:
            return
        qrc_on_air()

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
        
def btn_evt_off_air(btn):
    if btn.value == True:
        qrc_off_air()


def init_buttons_evt():
    tp_add_watcher(DV_TP, 2, 7, toggle_chime)
    tp_add_watcher(DV_TP, 2, 3, qrc_count_up_page_time)
    tp_add_watcher(DV_TP, 2, 4, qrc_count_down_page_time)
    tp_add_watcher(DV_TP, 2, 10, btn_reset_all_relay)
    tp_add_watcher(DV_TP, 2, 11, btn_evt_on_air)
    tp_add_watcher(DV_TP, 2, 12, btn_evt_off_air)