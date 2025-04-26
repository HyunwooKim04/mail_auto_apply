import imaplib
import email
import smtplib
import os
import random
from email.mime.text import MIMEText
import time

# === Email Settings ===
IMAP_HOST = 'imap.gmail.com'
SMTP_HOST = 'smtp.gmail.com'
EMAIL = 'sarah20000924@gmail.com'
APP_PASSWORD = 'jmuo kxqg zcaw cuxs'

# === HTML file path for the start scene
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_REPORT_PATH = os.path.join(BASE_DIR, "missing-report.html")

# === State Flags
startFlag = False
currentScene = 1

# === Scene keywords and responses
scene_keywords = {
    1: "key",
    2: "book",
    3: "memo",
    4: "calendar",
    5: "brown shoes"
}

scene_replies = {
    1: "I looked through the keys… and it seems like just one is missing—the warehouse key!\nWhy would Mom take that one...? Anyway, good job. Tell K \'Let's move to warehouse.\"",
    2: "I checked, and that book… it looks like it was borrowed from the local library near Mom’s house.\nMom might’ve gone there. Tell K \'Let's move to the library.\"",
    3: "K said it was Mom’s handwriting...? I double-checked—it’s not hers.\nAnyway, someone saw her near her office instead. Tell K \'Let's move to the office.\"",
    4: "That note on the calendar? Probably nothing. Mom used to scribble weird things.\nThere’s a changing room next to her office—let’s check that instead. Tell K \'Let's move to the changing room.\"",
    5: "The soil on those shoes... it came from the hill behind the office. Mom might be there.\nPlease go now, and if you find her, stay there. I’m on my way! Tell K \'Let's move to the mountain.\""
}

default_reply = [
    "Hmm... I'm not sure this is connected to Mom's disappearance. Maybe check again?",
    "I don’t think this has anything to do with the case… Try looking somewhere else.",
    "That doesn't seem relevant. We need to stay focused—look for more clues.",
    "I’ve gone over it, and it feels unrelated. Let's keep searching.",
    "That might just be a distraction. There has to be something else.",
    "This doesn’t seem important right now. Maybe check a different clue?",
    "I can't see how this ties into what happened to Mom. Could you look again?",
    "Doesn’t look related… Maybe it’s something else nearby?",
    "That feels off. We need something more concrete.",
    "I’ve looked at this from every angle, and it’s not giving us anything useful.",
    "We need something stronger. This doesn’t feel like the right lead.",
    "I get why you'd think that’s relevant, but it might just be a coincidence.",
    "No signs this is part of the case. Let's keep moving.",
    "Let’s not get sidetracked. There must be a better clue somewhere.",
    "We’re missing something… but I don’t think it’s this."
]


# === Email sending function
def send_email(to, subject, body, is_html=False):
    msg = MIMEText(body, "html" if is_html else "plain")
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = to

    with smtplib.SMTP(SMTP_HOST, 587) as s:
        s.starttls()
        s.login(EMAIL, APP_PASSWORD)
        s.sendmail(EMAIL, to, msg.as_string())

# === Check unread mail for a given keyword, return True if matched
def check_mail(expected_keyword, reply_text, html_path=None):
    imap = imaplib.IMAP4_SSL(IMAP_HOST)
    imap.login(EMAIL, APP_PASSWORD)
    imap.select('inbox')

    status, messages = imap.search(None, 'UNSEEN')
    for num in messages[0].split():
        status, data = imap.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        message = email.message_from_bytes(raw_email)

        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = message.get_payload(decode=True).decode()

        sender = email.utils.parseaddr(message['From'])[1]
        subject = message['Subject']

        if expected_keyword in body.strip().lower():
            print(f"✅ Matched '{expected_keyword}' from {sender}")

            # Send HTML if provided
            if html_path:
                with open(html_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                send_email(sender, f"Re: {subject}", html_content, is_html=True)
            else:
                send_email(sender, f"Re: {subject}", reply_text)

            imap.logout()
            return True

        else:
            print(f"❌ Keyword '{expected_keyword}' not found in message from {sender}")
            random_reply = random.choice(default_reply)
            send_email(sender, f"Re: {subject}", random_reply)

    imap.logout()
    return False

# === Start Scene (HTML auto-reply)
def start():
    global startFlag
    print("📨 Waiting for 'Hi' to begin...")
    if check_mail("hi", "", html_path=HTML_REPORT_PATH):
        startFlag = True

# === Scene 1~5
def handle_scene(scene_num):
    keyword = scene_keywords[scene_num]
    reply = scene_replies[scene_num]
    print(f"📨 Scene {scene_num} waiting...")
    return check_mail(keyword, reply)

# === Main execution loop
while not startFlag:
    start()
    time.sleep(5)

while currentScene <= 5:
    if handle_scene(currentScene):
        currentScene += 1
    time.sleep(5)

print("🎉 All scenes completed.")

