import imaplib
import email
from email.header import decode_header
import json
import time
import re
import datetime
import renew

ACCOUNTS_FILE_PATH = 'accounts.json'
CHECK_INTERVAL = 5 
MAX_EMAIL_AGE = 60  # anything older than 60 secs is considered stale and should be ignored

def get_credentials(type):
    with open(ACCOUNTS_FILE_PATH, 'r') as file:
        accounts = json.load(file)

    for account in accounts:
        if account['type'] == type:
            return account['email'], account['password']
    raise ValueError(f"{type.capitalize()} email account not found in accounts.json")

def check_for_renewal_emails(initial_time):
    # print("Connecting to the Gmail server...", flush=True)
    gmail_user, gmail_pass = get_credentials('catchall')
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(gmail_user, gmail_pass)
    mail.select("inbox")

    print("Looking for renewal notice emails...", flush=True)

    try:
        status, messages = mail.search(None, '(FROM "*@noip.com" UNSEEN SUBJECT "ACTION REQUIRED:")') # reads the forwarded renewal notice from the catchall email
        if status != 'OK':
            print("Error searching for emails.", flush=True)
            return set()

        email_ids = messages[0].split()
        # print(f"Email IDs: {email_ids}", flush=True)

        accounts_to_renew = set()

        if email_ids:
            for email_id in reversed(email_ids):
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                if status != 'OK':
                    print("Error fetching the email.", flush=True)
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        email_subject = decode_header(msg["subject"])[0][0]

                        if isinstance(email_subject, bytes):
                            email_subject = email_subject.decode()

                        print(f"Parsing email with subject: {email_subject}", flush=True)

                        email_date = msg["date"]
                        email_datetime = email.utils.parsedate_to_datetime(email_date)
                        email_datetime = email_datetime.astimezone(datetime.timezone.utc)
                        current_time = datetime.datetime.now(datetime.timezone.utc)

                        print(f"Email date: {email_datetime}, Current time: {current_time}", flush=True)

                        if email_datetime > initial_time and (current_time - email_datetime).total_seconds() < MAX_EMAIL_AGE:
                            email_from = msg["from"]
                            match = re.search(r'<(.+?)>', email_from)
                            if match:
                                email_address = match.group(1)
                                accounts_to_renew.add(email_address)
                        else:
                            print(f"Email is older than {MAX_EMAIL_AGE} seconds or before the script started, continuing search.", flush=True)
    except Exception as e:
        print(f"Error checking renewal emails: {e}", flush=True)
    finally:
        mail.logout()

    return accounts_to_renew

def renew_matching_accounts(accounts_to_renew):
    with open(ACCOUNTS_FILE_PATH, 'r') as file:
        accounts = json.load(file)

    for account in accounts:
        if account['email'] in accounts_to_renew and account['type'] == 'domain':
            print(f"Renewing account for {account['email']}", flush=True)
            renew.run_docker_command(account['email'], account['password'])

if __name__ == "__main__":
    initial_time = datetime.datetime.now(datetime.timezone.utc)
    while True:
        accounts_to_renew = check_for_renewal_emails(initial_time)
        if accounts_to_renew:
            renew_matching_accounts(accounts_to_renew)
        else:
            print("No renewal emails found — monitoring..", flush=True)
        
        time.sleep(CHECK_INTERVAL)
