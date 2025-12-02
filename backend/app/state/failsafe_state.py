# backend/app/state/failsafe_state.py

# This file stores the drone's failsafe state in memory.
# Other modules import these functions.

failsafe_state = {
    "action": "NONE",   # can be NONE / HOLD / LAND / KILL
    "reason": None
}

def get_failsafe():
    """Return current failsafe state."""
    return failsafe_state

def set_failsafe(action: str, reason: str = None):
    """Update failsafe state."""
    failsafe_state["action"] = action
    failsafe_state["reason"] = reason

def reset_failsafe():
    """Reset failsafe back to normal."""
    failsafe_state["action"] = "NONE"
    failsafe_state["reason"] = None
