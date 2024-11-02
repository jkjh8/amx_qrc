# ---------------------------------------------------------------------------- #
# from config import venue_name, zone_name, DV_TP
from modules.lib_tp import *
from config import *
# from mojo import context
# from UIMenu import UIMenu

# ---------------------------------------------------------------------------- #
# DV_MUSE = context.devices.get("idevice")


# ---------------------------------------------------------------------------- #
def tp_set_btn_show_hide(tp, port, addr, state):
    state_str = 1 if state else 0
    tp.port[port].send_command(f"^SHO-{addr},{state_str}")
    tp.port[port].send_command(f"^ENA-{addr},{state_str}")


def convert_text_to_unicode(text):
    return "".join(format(ord(char), "04X") for char in text)


def tp_set_btn_text_unicode(tp, port, addr, text):
    tp.port[port].send_command(f"^UNI-{addr},0," + text)

def btn_refresh_chime_btn():
    tp_set_button(DV_TP, 2, 7, qrc_chime)
    
def btn_refresh_zone_on_air_btn():
    for idx in range(1, num_of_zones + 1):
        tp_set_button(DV_TP, 2, idx + 50, qrc_zone_on_air_status[idx - 1])

def btn_refresh_zone_selected_btn(idx):
    tp_set_button(DV_TP, 2, idx + 20, tp_qrc_on_air_zone_list[idx - 1])

def btn_refresh_all_zone_selected_btn():
    for idx in range(1, num_of_zones + 1):
        btn_refresh_zone_selected_btn(idx)
        
def btn_refresh_is_on_air_btn():
    tp_set_button(DV_TP, 2, 11, qrc_is_on_air)
    tp_set_button(DV_TP, 2, 12, not qrc_is_on_air)
    
def tp_update_gain(idx):
    DV_TP.port[2].send_command("^TXT-" + str(101 + idx) + ",0," + str(qrc_zone_gain_status[idx]) + "dB")
    
def tp_add_watcher(tp, port, btn, callback):
    """
    tp_add_watcher 함수는 tp 객체의 모든 요소에 대해 지정된 port와 btn에 대한 callback 함수를 등록합니다.
    """
    try:
        if not tp.isOnline():
            return
        tp.port[port].button[btn].watch(callback)
    except Exception as e:
        logger.error(f"Error adding watcher: {e}")

    
# from config import venue_name, zone_name


# def handle_DV_TP_online(_):
#     UIMenu(DV_TP)
#     tp_set_btn_text_unicode(DV_TP, 2, 1, convert_text_to_unicode(text=venue_name))
#     for zone_id, zone_name in enumerate(zone_name):
#         tp_set_btn_text_unicode(DV_TP, 2, zone_id + 20 + 1, convert_text_to_unicode(zone_name))


# ---------------------------------------------------------------------------- #
# DV_TP.online(handle_DV_TP_online)
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
