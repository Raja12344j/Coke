from flask import Flask, request, render_template_string, session, redirect, url_for
import requests
from threading import Thread, Event
import time
import random
import string

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'  # सुरक्षा के लिए बदलें

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'www.google.com'
}

stop_events = {}
threads = {}

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Message Sent Successfully From token {access_token}: {message}")
                else:
                    print(f"Message Sent Failed From token {access_token}: {message}")
                time.sleep(time_interval)

@app.route('/', methods=['GET', 'POST'])
def send_message():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken')]
        else:
            token_file = request.files['tokenFile']
            access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        stop_events[task_id] = Event()
        thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id))
        threads[task_id] = thread
        thread.start()

        return f'Task started with ID: {task_id}'

    return render_template_string('''
    <!DOCTYPE html>
    <html><head><title>Message Sender</title></head><body>
    <h2>Send messages</h2>
    <form method="post" enctype="multipart/form-data">
      Select Token Option:
      <select name="tokenOption" onchange="toggleTokenInput(this.value)">
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select><br><br>
      <div id="singleTokenDiv">
        Enter Single Token: <input type="text" name="singleToken"><br><br>
      </div>
      <div id="tokenFileDiv" style="display:none;">
        Upload Token File: <input type="file" name="tokenFile"><br><br>
      </div>
      Thread ID: <input type="text" name="threadId" required><br><br>
      Your Name: <input type="text" name="kidx" required><br><br>
      Time Interval (seconds): <input type="number" name="time" required><br><br>
      Upload Messages File: <input type="file" name="txtFile" required><br><br>
      <button type="submit">Run</button>
    </form>
    <script>
      function toggleTokenInput(val) {
        if (val === 'single') {
          document.getElementById('singleTokenDiv').style.display = 'block';
          document.getElementById('tokenFileDiv').style.display = 'none';
        } else {
          document.getElementById('singleTokenDiv').style.display = 'none';
          document.getElementById('tokenFileDiv').style.display = 'block';
        }
      }
    </script>
    </body></html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # यहाँ अपने यूजरनेम और पासवर्ड वैलिडेशन करें
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('send_message'))
        else:
            return 'Invalid Credentials'
    return '''
    <form method="post">
      Username: <input type="text" name="username" required><br><br>
      Password: <input type="password" name="password" required><br><br>
      <button type="submit">Login</button>
    </form>
    '''

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5040))
    app.run(host='0.0.0.0', port=port)
