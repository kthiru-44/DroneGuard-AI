attack_state = {
    "mode": None,
    "params": {}
}

def set_attack(mode, params):
    attack_state["mode"] = mode
    attack_state["params"] = params

def clear_attack():
    attack_state["mode"] = None
    attack_state["params"] = {}

def get_attack():
    return attack_state
