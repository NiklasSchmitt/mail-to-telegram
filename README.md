# mail-to-telegram
This bot is polling an IMAP mailaccount for new mails. If a new mail is detected, it's forwarded to an specified telegram channel and deleted from the mail inbox. It's just a project of some hours.


original source: https://git.hack-hro.de/oyla/mail-to-telegram-bot/-/tree/master/ but I've done some improvements for my own use

---

## Configuration

- `apt install python3 python3-python-telegram-bot`
- Use [BotFather](https://t.me/botfather) to create your new bot and get your bot token
- `cp mail-to-telegram-bot.json.example mail-to-telegram-bot.json`, then set your configurations
- Run with `python3 mail-to-telegram-bot.py`
- Invite your bot to your channel, or talk directly to her in Telegram. 
- Get the ID of your chat with `/chatid`. Insert it to your configuration, so the bot just talks to your allowed chat.
  - this was very usefull for me to find out the chatid: https://stackoverflow.com/a/38388851
- additional: create a cronjob or something else that the script will get started again after a reboot

## Security

Not really happening here, don't use it in critcal situations. 
