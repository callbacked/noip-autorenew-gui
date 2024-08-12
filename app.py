from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, send_file
import json
import subprocess
import threading
import os

app = Flask(__name__)

ACCOUNTS_FILE_PATH = 'accounts.json'
AUTO_RENEW_SCRIPT = 'renew-auto.py'
MANUAL_RENEW_SCRIPT = 'renew.py'
RENEWAL_OUTPUT_FILE = 'manual_renew_output.txt'
is_renewal_running = False

def start_auto_renew():
    global is_renewal_running
    is_renewal_running = True
    process = subprocess.Popen(['python', AUTO_RENEW_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in iter(process.stdout.readline, ''):
        print(line, end='')  
    process.stdout.close()
    process.stderr.close()
    process.wait()
    is_renewal_running = False

def generate_console_output():
    process = subprocess.Popen(['python', AUTO_RENEW_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                yield f"data: {line}\n\n"
        for line in iter(process.stderr.readline, ''):
            if line:
                yield f"data: {line}\n\n"
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
    finally:
        process.stdout.close()
        process.stderr.close()
        process.wait()

@app.route('/')
def index():
    with open(ACCOUNTS_FILE_PATH, 'r') as file:
        accounts = json.load(file)
    
    catchall = next((account for account in accounts if account.get('type') == 'catchall'), None)
    domains = [account for account in accounts if account.get('type') == 'domain']

    return render_template('index.html', catchall=catchall, domains=domains)

@app.route('/add_account', methods=['POST'])
def add_account():
    email = request.form['email']
    password = request.form['password']
    account_type = request.form.get('type', 'domain')
    
    with open(ACCOUNTS_FILE_PATH, 'r') as file:
        accounts = json.load(file)
    
    if account_type == 'catchall':
        accounts = [account for account in accounts if account.get('type') != 'catchall']
    
    accounts.append({'email': email, 'password': password, 'type': account_type})
    
    with open(ACCOUNTS_FILE_PATH, 'w') as file:
        json.dump(accounts, file, indent=2)
    
    return redirect(url_for('index'))

@app.route('/delete_account/<email>', methods=['POST'])
def delete_account(email):
    with open(ACCOUNTS_FILE_PATH, 'r') as file:
        accounts = json.load(file)
    
    accounts = [account for account in accounts if account['email'] != email]
    
    with open(ACCOUNTS_FILE_PATH, 'w') as file:
        json.dump(accounts, file, indent=2)
    
    return redirect(url_for('index'))

@app.route('/renew', methods=['POST'])
def renew():
    global is_renewal_running
    is_renewal_running = True
    def run_manual_renew():
        with open(RENEWAL_OUTPUT_FILE, 'w') as file:
            process = subprocess.Popen(['python', MANUAL_RENEW_SCRIPT], stdout=file, stderr=file, text=True)
            process.wait()
        global is_renewal_running
        is_renewal_running = False
    threading.Thread(target=run_manual_renew, daemon=True).start()
    return jsonify({'status': 'Manual renewal started'})

@app.route('/manual_renew_log')
def manual_renew_log():
    try:
        with open(RENEWAL_OUTPUT_FILE, 'r') as file:
            log = file.read()
        return jsonify({'log': log})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/is_renewal_running')
def is_renewal_running_status():
    return jsonify({'running': is_renewal_running})

@app.route('/events')
def events():
    return Response(generate_console_output(), content_type='text/event-stream')

@app.route('/export_accounts')
def export_accounts():
    return send_file(ACCOUNTS_FILE_PATH, as_attachment=True)

@app.route('/import_accounts', methods=['POST'])
def import_accounts():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.json'):
        file.save(ACCOUNTS_FILE_PATH)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    threading.Thread(target=start_auto_renew, daemon=True).start()
    app.run(host='0.0.0.0')
