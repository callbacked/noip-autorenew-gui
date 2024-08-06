from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import json
import subprocess
import threading

app = Flask(__name__)

ACCOUNTS_FILE_PATH = 'accounts.json'
AUTO_RENEW_SCRIPT = 'renew-auto.py'
MANUAL_RENEW_SCRIPT = 'renew.py'

def start_auto_renew():
    process = subprocess.Popen(['python', AUTO_RENEW_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in iter(process.stdout.readline, ''):
        print(line, end='')  
    process.stdout.close()
    process.stderr.close()
    process.wait()

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
    subprocess.Popen(['python', MANUAL_RENEW_SCRIPT])
    return jsonify({'status': 'Manual renewal started'})

@app.route('/events')
def events():
    return Response(generate_console_output(), content_type='text/event-stream')

if __name__ == '__main__':
    threading.Thread(target=start_auto_renew, daemon=True).start()
    app.run(host='0.0.0.0')