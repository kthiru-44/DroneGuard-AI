# utils/failsafe/failsafe_engine.py

from app.state import failsafe_state

class FailsafeEngine:
    """
    Central engine that decides when to activate or deactivate failsafe modes.
    Highly modular, easy to extend with new detection rules.
    """

    def __init__(self):
        pass

    # ---------------------------------------------
    # PUBLIC API
    # ---------------------------------------------
    def process_detection(self, detection: dict):
        """
        Called by detectors every time new detection results arrive.
        Example detection payload:
        {
            "attack_detected": True,
            "attack_type": "GPS_SPOOF",
            "severity": "high"
        }
        """

        if not detection.get("attack_detected", False):
            return  # No attack → ignore safely

        attack_type = detection.get("attack_type")
        severity = detection.get("severity", "low")

        # ----- AUTO FAILSAFE HANDLING -----
        state = failsafe_state.get_state()
        auto_mode = state.get("auto_mode", False)

        if auto_mode:
            self._auto_failsafe_logic(attack_type, severity)
        else:
            # Manual mode → only report attack, NO intervention
            print(f"[Failsafe] Attack detected ({attack_type}) but AUTO FAILSAFE is OFF.")
            return

    def clear_failsafe(self):
        """
        Called when drone recovers or operator manually clears failsafe.
        """
        failsafe_state.deactivate()
        print("[Failsafe] Cleared.")

    # ---------------------------------------------
    # INTERNAL LOGIC (Private Methods)
    # ---------------------------------------------
    def _auto_failsafe_logic(self, attack_type: str, severity: str):
        """
        Automatic failsafe decision tree.
        """

        if attack_type == "GPS_SPOOF":
            self._handle_gps_spoof(severity)

        elif attack_type == "HEADING_MISMATCH":
            self._handle_heading_attack(severity)

        elif attack_type == "IMU_INCONSISTENT":
            self._handle_imu_failure(severity)

        elif attack_type == "PHYSICS_FAIL":
            self._handle_physics_violation(severity)

        else:
            print(f"[Failsafe] Unknown attack type: {attack_type}")

    # ---------------------------------------------
    # FAILSAFE RULES PER ATTACK TYPE
    # ---------------------------------------------
    def _handle_gps_spoof(self, severity: str):
        """
        GPS Spoof handling logic.
        """
        print(f"[Failsafe] GPS Spoof detected (severity={severity})")

        if severity == "high":
            failsafe_state.activate("GPS_SPOOF_RTH")
            print("[Failsafe] → Auto Return-To-Home triggered.")
        else:
            failsafe_state.activate("GPS_SPOOF_HOLD")
            print("[Failsafe] → Auto Position Hold triggered.")

    def _handle_heading_attack(self, severity: str):
        print(f"[Failsafe] Heading mismatch detected (severity={severity})")

        if severity == "high":
            failsafe_state.activate("HEADING_EMERGENCY_LAND")
            print("[Failsafe] → Emergency Land triggered.")
        else:
            failsafe_state.activate("HEADING_HOLD")
            print("[Failsafe] → Holding position.")

    def _handle_imu_failure(self, severity: str):
        print(f"[Failsafe] IMU inconsistency detected (severity={severity})")

        # IMU errors are dangerous → force immediate land
        failsafe_state.activate("IMU_EMERGENCY_LAND")
        print("[Failsafe] → EMERGENCY LAND activated due to IMU failure.")

    def _handle_physics_violation(self, severity: str):
        print(f"[Failsafe] Physics violation detected (severity={severity})")

        failsafe_state.activate("PHYSICS_HOLD")
        print("[Failsafe] → Holding position due to physics anomaly.")
