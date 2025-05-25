from datetime import datetime, timezone
import random
import requests
from tls_client import Session
from config import HEADERS, DC_MAIN_TOKEN, SOFI_BOT_ID, SOFI_CHANNEL, SOFI_GUILD_ID
from utils import webhook_log, ordermap

tls_session = Session(client_identifier="chrome_115", random_tls_extension_order=True)

def post_message(message: str, token: str = DC_MAIN_TOKEN):
    header = HEADERS
    header["authorization"] = token
    url = f"https://discord.com/api/v9/channels/{SOFI_CHANNEL}/messages"
    resp = tls_session.post(url, json={"content": message}, headers=header)
    status = "Success" if resp.status_code == 200 else "Error"
    webhook_log(f"Message response code {resp.status_code}", status)
    return resp.status_code

def fetch_latest_drop(strict: bool = False):
    try:
        messages = requests.get(f"https://discord.com/api/v9/channels/{SOFI_CHANNEL}/messages?limit=5", headers=HEADERS).json()
        for msg in messages:
            if msg.get("author", {}).get("id") == SOFI_BOT_ID and msg.get("components"):
                if not strict: 
                    return msg
                timesent = msg.get("timestamp")
                timestamp = datetime.fromisoformat(timesent)
                now = datetime.now(timezone.utc)
                delta = now - timestamp
                if delta.seconds < 30: 
                    return msg
    except Exception as e:
        webhook_log(f"Error fetching drop: {e}", "Error")
    return None

def grab_card(drop_msg: dict, index: int | None = None, token: str = DC_MAIN_TOKEN):
    header = HEADERS
    header["authorization"] = token

    random_index = random.randint(0, 2)
    try:
        buttons = drop_msg["components"][0]["components"]
        choice = buttons[random_index]
        choosen_index = random_index
        
        if index:
            choice = buttons[index]
            choosen_index = index
            
        webhook_log(f"Attempting to grab {choosen_index+1}{ordermap[choosen_index+1]} card")

        payload = {
            "type": 3,
            "application_id": SOFI_BOT_ID,
            "guild_id": SOFI_GUILD_ID,
            "channel_id": SOFI_CHANNEL,
            "message_id": drop_msg["id"],
            "session_id": "super-kuul-session-id",
            "data": {"component_type": 2, "custom_id": choice["custom_id"]}
        }
        r = requests.post("https://discord.com/api/v9/interactions", json=payload, headers=header)
        return r.status_code, drop_msg.get('attachments')[0].get('url'), random_index
    except Exception as e:
        webhook_log(f"Grab error: {e}", "Error")
        return None, None, None