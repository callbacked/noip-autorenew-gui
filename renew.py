import os
import subprocess
import json
import imaplib
import email
from email.header import decode_header
import re
import pty
import time
from datetime import datetime, timezone
import select

ACCOUNTS_FILE_PATH = 'accounts.json'
WAIT_TIME = 30  
MAX_EMAIL_AGE = 60  # anything older than 60 secs is considered stale and should be ignored

def get_totp_code():
    initial_time = datetime.now(timezone.utc)
    end_time = time.time() + WAIT_TIME

    while time.time() < end_time:
        print("Connecting to the Gmail server...")
        gmail_user, gmail_pass = get_credentials('catchall')
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, gmail_pass)
        mail.select("inbox")

        print("Waiting for incoming TOTP code...")

        try:
            status, messages = mail.search(None, '(FROM "*@noip.com" UNSEEN SUBJECT "No-IP Verification Code:")') # reads the forwarded OTP code from the catchall email (IF NEEDED)
            if status != 'OK':
                print("Error searching for emails.")
                break

            email_ids = messages[0].split()
            #print(f"Email IDs: {email_ids}")

            if email_ids:
                for email_id in reversed(email_ids):
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    if status != 'OK':
                        print("Error fetching the email.")
                        break

                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            email_subject = decode_header(msg["subject"])[0][0]

                            if isinstance(email_subject, bytes):
                                email_subject = email_subject.decode()

                            print(f"Parsing email with subject: {email_subject}")

                            email_date = msg["date"]
                            email_datetime = email.utils.parsedate_to_datetime(email_date)
                            if email_datetime > initial_time and (datetime.now(timezone.utc) - email_datetime).total_seconds() < MAX_EMAIL_AGE:
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        if part.get_content_type() == "text/plain":
                                            email_body = part.get_payload(decode=True).decode()
                                            break
                                else:
                                    email_body = msg.get_payload(decode=True).decode()

                                print(f"Email body: {email_body}")

                                totp_code = extract_totp_code_from_email(email_body)

                                if totp_code:
                                    print(f"Extracted TOTP code: {totp_code}")
                                    mail.logout()
                                    return totp_code
                            else:
                                print(f"Email is older than {MAX_EMAIL_AGE} seconds or before the script started, continuing search.")
        except Exception as e:
            print(f"Error getting TOTP code: {e}")

        mail.logout()
        time.sleep(5)  

    print("No new OTP code received.")
    return None

def extract_totp_code_from_email(email_body):
    match = re.search(r'\b\d{6}\b', email_body)
    if match:
        return match.group(0)
    return None

def run_docker_command(email, password):
    print(f"Running Docker Command for {email} at {datetime.now()}")

    master_fd, slave_fd = pty.openpty()
    cmd = f"docker run --rm -it simaofsilva/noip-renewer:latest {email} {password}"
    process = subprocess.Popen(cmd, shell=True, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True)

    output = ""
    start_time = time.time()
    max_runtime = 300  #

    try:
        while True:
            if time.time() - start_time > max_runtime:
                print(f"Maximum runtime of {max_runtime} seconds exceeded. Terminating.")
                break

            try:
                rlist, _, _ = select.select([master_fd], [], [], 5) 
                if not rlist:
                    print("No output for 5 seconds, checking if process has ended")
                    if process.poll() is not None:
                        print("Process has ended")
                        break
                    continue

                chunk = os.read(master_fd, 1024).decode('utf-8')
                if not chunk:
                    print("End of output")
                    break
                
                output += chunk
                print(f"Docker output: {chunk.strip()}")

                if "Enter OTP code:" in chunk:
                    print("OTP prompt detected, fetching TOTP code...")
                    totp_code = get_totp_code()
                    if totp_code:
                        print(f"Providing TOTP code: {totp_code}")
                        os.write(master_fd, f"{totp_code}\n".encode())
                    else:
                        print(f"Failed to get TOTP code for {email}")
                        break

                if "Logging off" in chunk:
                    print("Detected 'Logging off', waiting for process to end")
                    end_time = time.time() + 10  
                    while time.time() < end_time:
                        if process.poll() is not None:
                            print("Process has ended after logging off")
                            break
                        time.sleep(1)
                    break

            except Exception as e:
                print(f"Error reading output: {e}")
                if process.poll() is not None:
                    print("Process has ended")
                    break

    finally:
        os.close(master_fd)
        os.close(slave_fd)
        if process.poll() is None:
            print("Forcibly terminating the process")
            process.kill()
        else:
            print("Process has already terminated")

    process.wait(timeout=10)  
    print("Docker command finished.")
    confirmed_hosts = [line for line in output.split('\n') if line.strip().endswith("confirmed") and line.startswith("Host")]
    print("Confirmed hosts:", confirmed_hosts)
    

def get_credentials(type):
    with open(ACCOUNTS_FILE_PATH, 'r') as file:
        accounts = json.load(file)

    for account in accounts:
        if account['type'] == type:
            return account['email'], account['password']
    raise ValueError(f"{type.capitalize()} email account not found in accounts.json")

def read_accounts_and_renew():
    with open(ACCOUNTS_FILE_PATH, 'r') as file:
        accounts = json.load(file)
    
    print(f"Total accounts to process: {len(accounts)}")
    
    for i, account in enumerate(accounts, 1):
        if account['type'] == 'domain':
            print(f"Processing account {i} of {len(accounts)}: {account['email']}")
            run_docker_command(account['email'], account['password'])
            print(f"Finished processing account: {account['email']}")
    
    print("All domain accounts processed.")

if __name__ == "__main__":
    read_accounts_and_renew()
