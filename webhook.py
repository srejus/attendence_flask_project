import requests
import logging
from typing import Dict

# -------------------------------------------------
# CONFIG – change only these
# -------------------------------------------------
DJANGO_WEBHOOK_URL = "http://77.93.152.241:9040/webhook"

DJANGO_WEBHOOK_URL = "http://77.93.152.241:9099/webhook"

# DJANGO_WEBHOOK_URL = "http://192.168.1.5:8000/webhook"
DJANGO_SHARED_SECRET = "CHANGE_THIS_SECRET"
TIMEOUT_SECONDS = 2

logger = logging.getLogger(__name__)


def send_attendance_webhook(payload: Dict) -> bool:
    print(f"\n\n===Sending Webhook====>{DJANGO_WEBHOOK_URL}\n\n")
    """
    Sends attendance data to Django via HTTP webhook.

    This function:
    - NEVER raises exceptions to caller
    - NEVER blocks longer than TIMEOUT_SECONDS
    - Returns True on success, False on failure

    Safe to call inside get_attendance().
    """

    try:
        logger.info("[Webhook] Sending attendance payload: %s", payload)

        response = requests.post(
            DJANGO_WEBHOOK_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {DJANGO_SHARED_SECRET}",
                "Content-Type": "application/json",
            },
            timeout=TIMEOUT_SECONDS,
        )

        if response.status_code != 200:
            print("WEBHOOK ERROR : ",response.text)
            logger.error(
                "[Webhook] Django rejected request | status=%s response=%s",
                response.status_code,
                response.text,
            )
            return False
        print("WEBHOOK SENT SUCCESSFULLY===\n\n\n")
        logger.info("[Webhook] Attendance forwarded successfully")
        return True

    except Exception as exc:
        logger.exception("[Webhook] Failed to send attendance webhook")
        return False
