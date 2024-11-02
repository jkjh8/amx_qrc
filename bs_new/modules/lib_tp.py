# ---------------------------------------------------------------------------- #
from mojo import context


# ---------------------------------------------------------------------------- #
def tp_get_device_state(tp):
    try:
        return tp.isOnline() is True
    except Exception as e:
        return False


# ---------------------------------------------------------------------------- #
def tp_add_watcher(tp, port, btn, callback):
    """
    tp_add_watcher 함수는 tp 객체의 모든 요소에 대해 지정된 port와 btn에 대한 callback 함수를 등록합니다.
    """
    try:
        if not tp_get_device_state(tp):
            return
        tp.port[port].button[btn].watch(callback)
    except Exception as e:
        context.log.error(f"Error adding watcher: {e}")


# ---------------------------------------------------------------------------- #
def tp_send_command(tp, idx_port, command):
    """
    tp_send_command 함수는 tp 객체의 모든 요소에 대해 지정된 idx_port command를 전송합니다.
    """
    try:
        if not tp_get_device_state(tp):
            # context.log.warn(f"tp_send_command() {tp=} {idx_port=} Device not running")
            return
        tp.port[idx_port].send_command(command)
    except Exception as e:
        context.log.error(f"Error sending command: {e}")


# ---------------------------------------------------------------------------- #
def tp_set_button(tp, idx_port, idx_btn, state):
    """
    tp_set_button 함수는 tp 객체의 모든 요소에 대해 지정된 port와 btn의 상태[켜짐|꺼짐] 를 설정합니다.
    """
    try:
        if not tp_get_device_state(tp):
            # context.log.warn(f"tp_set_button() {tp=} {idx_port=} {idx_btn=} Device not running")
            return
        tp.port[idx_port].channel[idx_btn].value = state
    except Exception as e:
        context.log.error(f"Error setting button {__name__=} {idx_port=} {idx_btn=} : {e}")


# ---------------------------------------------------------------------------- #
def tp_set_button_in_range(tp, port, idx_btn_start, idx_btn_range, idx_cond):
    """
    tp_set_button_in_range 함수는 tp 객체의 모든 요소에 대해 지정된 port와 btn의 상태[켜짐|꺼짐] 를 설정합니다.
    """
    for i, btn in enumerate(range(idx_btn_start, idx_btn_start + idx_btn_range + 1)):
        tp_set_button(tp, port, btn + 1, idx_cond == i + 1)


# ---------------------------------------------------------------------------- #
def tp_send_level(tp, idx_port, idx_btn, value):
    """
    tp_send_level 함수는 tp 객체의 모든 요소에 대해 지정된 port와 idx_btn에 value를 전송합니다.
    """
    try:
        if not tp_get_device_state(tp):
            context.log.warn(f"tp_send_level() {tp=} {idx_port=} {idx_btn=} Device not running")
            return
        tp.port[idx_port].level[idx_btn].value = value
    except Exception as e:
        context.log.error(f"Error setting level {__name__=} {idx_port=} {idx_btn=} : {e}")


# ---------------------------------------------------------------------------- #
def convert_text_to_unicode(text):
    """
    convert_text_to_unicode 함수는 주어진 텍스트를 유니코드 아스키로 변환하여 반환합니다.
    """
    return "".join(format(ord(char), "04X") for char in text)


# ---------------------------------------------------------------------------- #
def tp_set_button_text_unicode(tp, port, addr, text):
    """
    tp_set_button_text_unicode 함수는 tp 객체의 모든 요소에 대해 지정된 port, addr, text를 이용하여 버튼에 유니코드 텍스트를 표시합니다.
    """
    tp_send_command(tp, port, f"^UNI-{addr},0,{convert_text_to_unicode(text)}")


# ---------------------------------------------------------------------------- #
def tp_set_button_text(tp, port, addr, text):
    """
    tp_set_button_text 함수는 tp 객체의 모든 요소에 대해 지정된 port, addr, text를 이용하여 버튼에 텍스트를 표시합니다.
    """
    tp_send_command(tp, port, f"^TXT-{addr},0,{text}")


# ---------------------------------------------------------------------------- #
def tp_set_btn_show_hide(tp, port, addr, state):
    state_str = 1 if state else 0
    tp.port[port].send_command(f"^SHO-{addr},{state_str}")
    tp.port[port].send_command(f"^ENA-{addr},{state_str}")


# ---------------------------------------------------------------------------- #
def tp_set_page(tp, pagename):
    tp_send_command(tp, 1, f"^PGE-{pagename}")


# ---------------------------------------------------------------------------- #
def tp_show_popup(tp, popupname):
    tp_send_command(tp, 1, f"^PPN-{popupname}")


# ---------------------------------------------------------------------------- #
def tp_hide_all_popup(tp):
    tp_send_command(tp, 1, "^PPX")


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
