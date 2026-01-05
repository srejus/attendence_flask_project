import logging
from datetime import datetime

# Basic logger setup (prints to console)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


class DeviceStatus:
    """
    Debug-instrumented DeviceStatus.
    This class logs:
    - All constructor inputs
    - Any attribute assignment (even unknown ones)
    - WebSocket assignment
    - Full object state on demand
    """

    def __init__(self, device_sn=None, websocket=None, status=None, **kwargs):
        logger.debug("DeviceStatus.__init__ CALLED")

        logger.debug(
            "Constructor inputs | device_sn=%r, websocket=%r, status=%r",
            device_sn, websocket, status
        )

        if kwargs:
            logger.debug("Extra unexpected kwargs received: %r", kwargs)

        # Assign known fields
        self.device_sn = device_sn
        self.websocket = websocket
        self.status = status

        # Assign any extra incoming data dynamically
        for key, value in kwargs.items():
            setattr(self, key, value)

        logger.debug("DeviceStatus initialized successfully")
        self.dump()

    def __setattr__(self, name, value):
        """
        Intercepts ALL attribute assignments.
        This is the key part that prints EVERYTHING coming in.
        """
        logger.debug(
            "Attribute SET | %s = %r (type=%s)",
            name, value, type(value).__name__
        )
        super().__setattr__(name, value)

    def setWebSocket(self, websocket):
        logger.debug("setWebSocket CALLED with websocket=%r", websocket)
        self.websocket = websocket

    def update_status(self, status):
        logger.debug("update_status CALLED with status=%r", status)
        self.status = status

    def dump(self):
        """
        Dumps the full internal state of the object.
        """
        logger.debug("DeviceStatus.dump BEGIN")
        for k, v in vars(self).items():
            logger.debug("  %s = %r (type=%s)", k, v, type(v).__name__)
        logger.debug("DeviceStatus.dump END")

    def __repr__(self):
        return (
            f"<DeviceStatus "
            f"device_sn={self.device_sn!r} "
            f"status={self.status!r} "
            f"websocket={type(self.websocket).__name__ if self.websocket else None}>"
        )
