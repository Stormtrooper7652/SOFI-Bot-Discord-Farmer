import os
from dotenv import load_dotenv

load_dotenv()
DC_MAIN_TOKEN = os.getenv("DC_MAIN_TOKEN")				# First bot token
DC_SECONDARY_TOKEN = os.getenv("DC_SECONDARY_TOKEN")	# Second bot token
SOFI_CHANNEL = os.getenv("SOFI_CHANNEL_ID")				# Channel ID for Sofi commands
SOFI_BOT_ID = os.getenv("SOFI_BOT_ID")					# Numeric ID of the Sofi bot
SOFI_GUILD_ID = os.getenv("SOFI_GUILD_ID")				# Your server/guild ID
LOG_WEBHOOK_URL = os.getenv("LOG_WEBHOOK_URL")			# Webhook URL for logging
COMBINE_WEBHOOK_LOGS = True							# Weather to combine multiple logs into one request

if not all([DC_MAIN_TOKEN, DC_SECONDARY_TOKEN, SOFI_CHANNEL, SOFI_BOT_ID, SOFI_GUILD_ID, LOG_WEBHOOK_URL]):
	raise ValueError("Missing constant in .env")

HEADERS = {
	"authority": "discord.com",
	"method": "PATCH",
	"scheme": "https",
	"accept": "*/*",
	"accept-encoding": "gzip, deflate, br",
	"accept-language": "en-US",
	"authorization": "",
	"origin": "https://discord.com",
	"User-Agent": "Mozilla/5.0",
	"sec-ch-ua-mobile": "?0",
	"sec-fetch-dest": "empty",
	"sec-fetch-mode": "cors",
	"sec-fetch-site": "same-origin",
	"X-Discord-Locale": "en-US",
	"X-Discord-Timezone": "Asia/Calcutta",
}
