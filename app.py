from flask import Flask, request, make_response, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

# Simple login, जो कुकीज़ सेट करेगा
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # यहां यूजरनेम/पासवर्ड चेक करें (आप अपना लॉजिक लगा सकते हैं)
        if username == 'admin' and password == 'password':
            resp = make_response(redirect(url_for('send_message')))
            # यहाँ कुकी सेट करें (उदाहरण के लिए session कूकी)
            resp.set_cookie('session_id', 'your_session_value') 
            return resp
        else:
            return "Invalid credentials, try again"
    return '''
    <form method="post">
        Username: <input name="username" type="text"><br>
        Password: <input name="password" type="password"><br>
        <input type="submit" value="Login">
    </form>
    '''

# Authenticated पेज, जो कुकी पढ़ेगा
@app.route('/', methods=['GET', 'POST'])
def send_message():
    session_id = request.cookies.get('session_id')
    if not session_id or session_id != 'your_session_value':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # यहाँ अपनी मेसेजिंग लॉजिक डालें (आपके बॉट का कोड)
        return "Message processing started using your cookies session!"
    
    # GET पर यह फॉर्म दिखाएं
    return '''
    <form method="post">
        <label>Enter Your Cookies (optional):</label><br>
        <textarea name="cookies" rows="4" cols="50" placeholder="If needed"></textarea><br>
        <label>Thread ID:</label><br>
        <input name="threadId" type="text" required><br>
        <label>Your Name:</label><br>
        <input name="name" type="text" required><br>
        <label>Time Interval (seconds):</label><br>
        <input name="time" type="number" required><br><br>
        <input type="submit" value="Run Using Cookies">
    </form>
    '''

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('session_id')
    return resp

if __name__ == '__main__':
    app.run(debug=True)
