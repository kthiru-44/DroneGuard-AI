# config.py - safe defaults for local-only demo
from typing import Final

HOST: Final[str] = "127.0.0.1"   # local-only by default
PORT: Final[int] = 8000

# Safety: by default do not allow remote attack commands.
# If you intentionally want to allow LAN (for a controlled demo), change to True
# and understand the legal and ethical implications.
ALLOW_REMOTE_ATTACKS: Final[bool] = False

MDNS_SERVICE_NAME: Final[str] = "droneguard-demo-local"  # only for local demos (not advertised externally)
MDNS_HOSTNAME: Final[str] = "droneguard.local"
