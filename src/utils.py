import random
import requests
from config import COMBINE_WEBHOOK_LOGS, LOG_WEBHOOK_URL
from datetime import datetime, timedelta, timezone
from colorama import Fore, Back, Style

ordermap = {
    1: "st",
    2: "nd",
    3: "rd"
}

log_color_map = {
    "Info": Style.BRIGHT,
    "Warning": Fore.YELLOW,
    "Error": Fore.BLACK + Back.RED,
    "Success": Fore.GREEN
}

def get_skewed(a: float, b: float, skew_strength: float = 2.0) -> timedelta:
    if a >= b:
        raise ValueError("Parameter 'a' must be less than 'b'.")
    alpha = 2.0
    beta_param = skew_strength
    skewed_random = random.betavariate(alpha, beta_param)
    minutes = a + (b - a) * skewed_random
    return minutes

message_stack_type = "Info"
message_stack: list[str] = []

def flush_logs(clear: bool, url: str = LOG_WEBHOOK_URL):
    global message_stack, message_stack_type
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.isoformat()
    embed = {
        "title": message_stack_type,
        "description": '\n'.join(message_stack),
        "color": 0xFFC0CB,
        "timestamp": timestamp
    }
    payload = {"embeds": [embed]}

    if clear:
        message_stack = []
        message_stack_type = ""

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error flushing logs: {e}")
def webhook_log(message: str, status: str = "Info", url: str = LOG_WEBHOOK_URL):
    global message_stack, message_stack_type
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.isoformat()

    color = ""
    try:
        color = log_color_map[status]
    except Exception:
        pass

    print(f"{color}[{now_utc.strftime('%H:%M:%S.%f')[:-4]} - {status}]{Style.RESET_ALL}\t{message}")

    if COMBINE_WEBHOOK_LOGS:
        if (status != message_stack_type) or len(message_stack) >= 10:
            flush_logs(True, url)
            message_stack_type = status
        message_stack.append(message)
    else:
        embed = {
            "title": status,
            "description": message,
            "color": 0xFFC0CB,
            "timestamp": timestamp
        }
        payload = {"embeds": [embed]}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error sending log: {e}")