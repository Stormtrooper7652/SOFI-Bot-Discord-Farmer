import os
import time
import random
import threading
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from tls_client import Session

# ── Configuration ─────────────────────────────────────────────────────────────
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")                # Bot token
SOFI_CHANNEL = os.getenv("SOFI_CHANNEL_ID")               # Channel ID for Sofi commands
SOFI_BOT_ID = os.getenv("SOFI_BOT_ID")                    # Numeric ID of the Sofi bot
SOFI_GUILD_ID = os.getenv("SOFI_GUILD_ID")                # Your server/guild ID
SOFI_SESSION_COOKIE = os.getenv("SOFI_SESSION_COOKIE")    # connect.sid cookie for sofi.gg
LOG_WEBHOOK_URL = os.getenv("LOG_WEBHOOK_URL")            # Webhook URL for logging

if not all([DISCORD_TOKEN, SOFI_CHANNEL, SOFI_BOT_ID, SOFI_GUILD_ID, SOFI_SESSION_COOKIE, LOG_WEBHOOK_URL]):
    raise ValueError("Missing one of DISCORD_TOKEN, SOFI_CHANNEL_ID, SOFI_BOT_ID, SOFI_GUILD_ID, SOFI_SESSION_COOKIE, or LOG_WEBHOOK_URL in .env")

# ── Farming Cooldowns ─────────────────────────────────────────────────────────
DROP_COOLDOWN = timedelta(minutes=8)
GRAB_COOLDOWN = timedelta(minutes=4)

# ── Discord REST & Interaction Headers ────────────────────────────────────────
HEADERS = {
    "authority": "discord.com",
    "method": "PATCH",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US",
    "authorization": DISCORD_TOKEN,
    "origin": "https://discord.com",
    "User-Agent": "Mozilla/5.0",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "X-Discord-Locale": "en-US",
    "X-Discord-Timezone": "Asia/Calcutta",
}

# ── Initialize TLS session ────────────────────────────────────────────────────
tls_session = Session(client_identifier="chrome_115", random_tls_extension_order=True)

# ── Utility: Human-friendly timedelta ──────────────────────────────────────────
def format_timedelta(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    if total_seconds <= 0:
        return "now"
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours} {'hour' if hours==1 else 'hours'}")
    if minutes:
        parts.append(f"{minutes} {'min' if minutes==1 else 'mins'}")
    if not hours and seconds:
        parts.append(f"{seconds} {'sec' if seconds==1 else 'secs'}")
    return "in " + " and ".join(parts)

# ── Cat-like Logging ───────────────────────────────────────────────────────────
def log(message: str, status: str = "Info"):
    """
    Sends a Discord embed with a catty twist and prints locally.
    status can be: "Info", "Success", "Warning", "Error"
    """
    # Use timezone-aware UTC timestamp
    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.isoformat()
    embed = {
        "title": f"{status} • Nyan",
        "description": f"Purr... {message}",
        "color": 0xFFC0CB,  # Light Pink
        "timestamp": timestamp
    }
    payload = {"embeds": [embed]}
    try:
        requests.post(LOG_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Error sending log: {e}")
    # Local console print
    print(f"[{timestamp}] {status} > {message} (meow)")

# ── Discord Farming: Drops & Grabs ────────────────────────────────────────────
def post_message(cmd: str):
    log(f"Posting command '{cmd}' to Sofi, meow", "Info")
    url = f"https://discord.com/api/v9/channels/{SOFI_CHANNEL}/messages"
    resp = tls_session.post(url, json={"content": cmd}, headers=HEADERS)
    status = "Success" if resp.status_code == 200 else "Error"
    log(f"Response code {resp.status_code}", status)
    return resp.status_code


def fetch_latest_drop():
    log("Searching for latest drop, meow", "Info")
    url = f"https://discord.com/api/v9/channels/{SOFI_CHANNEL}/messages?limit=5"
    try:
        messages = requests.get(url, headers=HEADERS).json()
        for m in messages:
            if m.get("author", {}).get("id") == SOFI_BOT_ID and m.get("components"):
                log(f"Found drop: ID {m['id']}", "Success")
                return m
        log("No drop found, hiss...", "Warning")
    except Exception as e:
        log(f"Error fetching drop: {e}", "Error")
    return None


def click_grab_button(drop_msg: dict):
    log("Attempting to grab, meow", "Info")
    try:
        buttons = drop_msg["components"][0]["components"]
        choice = random.choice(buttons)
        payload = {
            "type": 3,
            "application_id": SOFI_BOT_ID,
            "guild_id": SOFI_GUILD_ID,
            "channel_id": SOFI_CHANNEL,
            "message_id": drop_msg["id"],
            "session_id": "sofi-farm-session",
            "data": {"component_type": 2, "custom_id": choice["custom_id"]}
        }
        r = requests.post("https://discord.com/api/v9/interactions", json=payload, headers=HEADERS)
        status = "Success" if r.status_code == 200 else "Error"
        log(f"Grabbed '{choice.get('label', 'unknown')}' - code {r.status_code}", status)
        return r.status_code, choice.get('label')
    except Exception as e:
        log(f"Grab error: {e}", "Error")
        return None, None


def farm_loop():
    last_drop = datetime.min.replace(tzinfo=timezone.utc)
    last_grab = datetime.min.replace(tzinfo=timezone.utc)

    while True:
        now = datetime.now(timezone.utc)
        if now - last_drop >= DROP_COOLDOWN:
            log("Time for 'sdrop', nya!", "Info")
            post_message("sdrop")
            last_drop = now
            time.sleep(random.uniform(1, 3))

        if now - last_grab >= GRAB_COOLDOWN:
            log("Time for 'sgrab', nya!", "Info")
            drop = fetch_latest_drop()
            if drop:
                code, item = click_grab_button(drop)
                if code:
                    log(f"sgrab done, got '{item}', purr~", "Success")
                last_grab = now
            else:
                log("Nothing to grab yet, mew...", "Warning")
            time.sleep(random.uniform(1, 3))

        # Calculate human-friendly wait times
        now2 = datetime.now(timezone.utc)
        until_drop = max(DROP_COOLDOWN - (now2 - last_drop), timedelta())
        until_grab = max(GRAB_COOLDOWN - (now2 - last_grab), timedelta())
        human_drop = format_timedelta(until_drop)
        human_grab = format_timedelta(until_grab)
        log(f"Next drop {human_drop}, next grab {human_grab}", "Info")
        time.sleep(5)

if __name__ == "__main__":
    log("Starting Sofi farm bot, purr purr", "Info")
    t1 = threading.Thread(target=farm_loop, daemon=True)
    t1.start()
    t1.join()
