from modules.lib_tp import *
from config import *

def tp_set_btn_show_hide(tp, port, addr, state):
    state_str = 1 if state else 0
    tp.port[port].send_command(f"^SHO-{addr},{state_str}")
    tp.port[port].send_command(f"^ENA-{addr},{state_str}")


def convert_text_to_unicode(text):
    return "".join(format(ord(char), "04X") for char in text)


def tp_set_btn_text_unicode(tp, port, addr, text):
    tp.port[port].send_command(f"^UNI-{addr},0," + text)

def btn_refresh_chime_btn():
    global page
    tp_set_button(DV_TP, 2, 7, page["qrc_chime"])
    
def btn_refresh_zone_on_air_btn():
    global page
    for idx in range(1, page["num_of_zones"] + 1):
        tp_set_button(DV_TP, 2, idx + 50, qrc_zones_onair[idx - 1])

def btn_refresh_zone_selected_btn(idx):
    global page
    tp_set_button(DV_TP, 2, idx + 20, qrc_zones[idx - 1])

def btn_refresh_all_zone_selected_btn():
    global page
    for idx in range(1, page["num_of_zones"] + 1):
        btn_refresh_zone_selected_btn(idx)
        
def btn_refresh_is_on_air_btn():
    global page
    tp_set_button(DV_TP, 2, 11, page["qrc_onair"])
    tp_set_button(DV_TP, 2, 12, not page["qrc_onair"])
    
def tp_update_gain(idx):
    global page
    DV_TP.port[2].send_command("^TXT-" + str(100 + idx) + ",0," + str(qrc_zones_gain[idx - 1]) + "dB")
    
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
