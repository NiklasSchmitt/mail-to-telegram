import os
import json
import logging

import imaplib
import email
from email.header import decode_header
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# get configuration
config = None
json_file_fullpath = os.path.join(os.path.dirname(__file__), 'mail-to-telegram-bot.json')
with open(json_file_fullpath) as json_file:
    config = json.load(json_file)

imap_host = config['imap_host']
imap_username = config['imap_username']
imap_password = config['imap_password']
imap_poll_interval = config['imap_poll_interval']
telegram_token = config['telegram_token']
telegram_chat_id = config['telegram_chat_id']

class MailContent:
    subject = ""
    from_ = ""
    body = ""
    # text/plain or text/html
    body_type = ""
    attachment = []

    def __str__(self):

        return "{}\n\n{}".format(self.subject, self.body)

class MailAttachment:
    name = None
    attachment_type = None
    data = None

# get the last message, return it and delete it from IMAP inbox
def progress_last_message():
    imap = imaplib.IMAP4(imap_host)
    imap.starttls()
    imap.login(imap_username, imap_password)

    status, messages = imap.select("INBOX")
    # number of top emails to fetch
    N = 1
    # total number of emails
    messages = int(messages[0])

    if messages:
        res, msg = imap.fetch("1", "(RFC822)")
        mail = MailContent()

        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode()
                # email sender
                from_ = msg.get("From")
                mail.subject = subject
                mail.from_ = from_
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            mail.body = body
                        elif "attachment" in content_disposition:
                            attachment = MailAttachment()
                            # download attachment
                            # filename = part.get_filename()
                            attachment.name = part.get_filename()
                            attachment.data = part.get_payload(decode=True)
                            mail.attachment.append(attachment)
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        mail.body = body
                if content_type == "text/html":
                    mail.body = body
                    mail.body_type = content_type
                imap.store("1", '+FLAGS', '\\Deleted')
                imap.expunge()
        return mail
    else:
        return None

    imap.close()
    imap.logout()

def show_chatid(update: Update, context: CallbackContext):
    update.effective_message.reply_html('Your chat id is <code>{}</code>.'.format(update.effective_chat.id))

def check_mails(context: CallbackContext):
    mail = progress_last_message()

    if mail:
      context.bot.send_message(chat_id=telegram_chat_id, text=str(mail))

def main():
    updater = Updater(telegram_token, use_context=True)

    jobq = updater.job_queue
    jobq.run_repeating(check_mails, interval=int(imap_poll_interval), first=3)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('chatid', show_chatid))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
    pass
