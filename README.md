# Sofi Selfbot – Auto Drop & Grab

A cozy Python-based selfbot that auto-drops and grabs in **Sofi.gg** on Discord.

---

## 💾 Requirements

### Python Version

* Python 3.9 or higher recommended

### Install dependencies

```bash
pip install tls-client python-dotenv requests
```

---

## ⚙️ .env Setup

Create a `.env` file in the root folder with the following:

```env
DISCORD_TOKEN=your_token_here
SOFI_CHANNEL_ID=your_channel_id_here
SOFI_BOT_ID=945759223522942996
SOFI_GUILD_ID=your_guild_id_here
SOFI_SESSION_COOKIE=your_sofi_cookie_here
LOG_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_here
```

### Description of variables:

* `DISCORD_TOKEN`: Your Discord account token (user token, not bot token)
* `SOFI_CHANNEL_ID`: The channel where you send `sdrop` and see Sofi messages
* `SOFI_BOT_ID`: Usually Sofi's ID – `945759223522942996`, but can be changed
* `SOFI_GUILD_ID`: Your server’s guild (server) ID
* `SOFI_SESSION_COOKIE`: Your Sofi session cookie (`connect.sid`) from browser
* `LOG_WEBHOOK_URL`: Optional. Logs actions and status updates to a pretty Discord webhook

> Be careful with your token and cookie – **keep this private**!

---

## How to Use

1. Fill in the `.env` file.
2. Install dependencies using `pip`.
3. Run the script:

   ```bash
   python selfbot.py
   ```
4. The bot will:

   * Drop with `sdrop` every 8 mins
   * Try to grab cards from Sofi drops every 4 mins
   * Log all actions to your terminal and webhook (if configured)

---

## Notes

* This is a selfbot. It **violates Discord's Terms of Service**. Use at your own risk.
* You should run this in a private server or alt account to avoid flagging.
* Customize time intervals or logging style in `selfbot.py`.

---

## Example Log Output

```
[2025-05-09T22:39:05Z] Info > Time for 'sdrop', nya!
[2025-05-09T22:39:08Z] Info > Time for 'sgrab', meow~
[2025-05-09T22:39:11Z] Success > sgrab done, got 'Emilia (Re:Zero)', purr~
[2025-05-09T22:39:14Z] Info > Next drop in 7 mins and 50 secs, next grab in 3 mins and 50 secs (meow)
```

---

## Stuff to add:
- Automatic bumping
- Multi-account support
- Best card picker
  Instead of picking a random card it will pick the best one.
- Favourite & Wishlisted cards
  If a wishlisted card comes up itl prioritize picking that card instead of the best one. 
- Automatic card burning
  If a card meets a specific requirement itl automatically burn the card. 
