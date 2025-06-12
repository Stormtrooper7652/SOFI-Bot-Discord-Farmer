import os
import random
import requests
import pytesseract
from PIL import Image
from tls_client import Session
from datetime import datetime, timezone
from config import HEADERS, DC_MAIN_TOKEN, SOFI_BOT_ID, SOFI_CHANNEL, SOFI_GUILD_ID
from utils import webhook_log, ordermap

tls_session = Session(client_identifier="chrome_115", random_tls_extension_order=True)

def post_message(message: str, token: str = DC_MAIN_TOKEN):
    header = HEADERS
    header["authorization"] = token
    url = f"https://discord.com/api/v9/channels/{SOFI_CHANNEL}/messages"
    resp = tls_session.post(url, json={"content": message}, headers=header)
    return resp.status_code

def fetch_latest_drop(strict: bool = True):
    try:
        messages = requests.get(f"https://discord.com/api/v9/channels/{SOFI_CHANNEL}/messages?limit=3", headers=HEADERS).json()
        for msg in messages:
            if msg.get("author", {}).get("id") == SOFI_BOT_ID and msg.get("components"):
                if not strict: 
                    return msg, None
                
                content = msg.get("content")
                if "Your **Drop** will be ready in" in content:
                    return None, "Delay"
                
                if "is **dropping** cards" in content: 
                    return msg, None
    except Exception as e:
        webhook_log(f"Error fetching drop: {e}", "Error")
    return None, None

def grab_card(drop_msg: dict, index: int | None = None, token: str = DC_MAIN_TOKEN):
    header = HEADERS
    header["authorization"] = token

    try:
        buttons = drop_msg["components"][0]["components"]
        choice = buttons[index]

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
        return r.status_code
    except Exception as e:
        webhook_log(f"Grab error: {e}", "Error")
        return None
    
def find_best_card(drop: dict):
    link = drop.get('attachments')[0].get('url')
    
    try:
        response = requests.get(link)
        response.raise_for_status()

        image_path = "drop.png"
        with open(image_path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        webhook_log(f"Failed to download drop image: {e}", "Error")
        return random.sample(range(0, 3), 2)
    
    image = Image.open(image_path)
    card_gen_regions = [
        (35, 430, 100, 452),
        (382, 430, 449, 452),
        (726, 430, 782, 452)
    ]
    cards = []

    for i, box in enumerate(card_gen_regions):
        cropped = image.crop(box).convert("L")
        text = pytesseract.image_to_string(cropped, config='--psm 7').strip()
        try: 
            cards.append(int(text))
        except ValueError: 
            cards.append(None)

    os.remove(image_path)

    valid_indices = [(i, val) for i, val in enumerate(cards) if val is not None]
    if not valid_indices:
        raise ValueError("No valid integers found in OCR")

    min_index = min(valid_indices, key=lambda x: x[1])[0]
    if None in cards:
        none_index = cards.index(None)
    else:
        sorted_valid = sorted(valid_indices, key=lambda x: x[1])
        if len(sorted_valid) >= 2:
            none_index = sorted_valid[1][0]
        else:
            none_index = min_index
    return min_index, none_index