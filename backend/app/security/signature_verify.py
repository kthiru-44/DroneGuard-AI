import json, base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

# Load PUBLIC key (copied from Pi — safe to share)
with open("public.pem", "r") as f:
    PUBLIC_KEY = RSA.import_key(f.read())

def verify_signature(payload: dict) -> bool:
    """Verify telemetry payload signature."""
    try:
        signature_b64 = payload.get("signature")
        if not signature_b64:
            return False

        signature = base64.b64decode(signature_b64)

        # create unsigned copy
        unsigned = payload.copy()
        unsigned.pop("signature", None)

        msg = json.dumps(unsigned, sort_keys=True).encode()
        h = SHA256.new(msg)

        pkcs1_15.new(PUBLIC_KEY).verify(h, signature)
        return True

    except Exception:
        return False
