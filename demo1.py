from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import time

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure secret key
# app.permanent_session_lifetime = timedelta(minutes=2)

# Mock user data (replace this with a proper user authentication mechanism)
users = {
    "shalini@gmail.com": {"password": "shalini"},
    # Add more users as needed
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and users[email]['password'] == password:
            session['email'] = email
            session.permanent = True
            return redirect(url_for('target'))
        else:
            return render_template('login.html', error='Invalid email or password')

    return render_template('login.html', error=None)

@app.route('/target', methods=['GET', 'POST'])
def target():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process the form data as needed
        target_name = request.form.get('target_name')
        target_id = request.form.get('target_id')
        target_details = request.form.get('target_details')

        # Add your logic to handle the form data

    return render_template('target.html')

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
    session.modified = True

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
