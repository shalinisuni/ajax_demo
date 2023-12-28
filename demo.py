from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import mysql.connector

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'shalini18031999@gmail.com'
app.config['MAIL_PASSWORD'] = 'glba witq lcvy bkom'
app.config['MAIL_DEFAULT_SENDER'] = 'shalini18031999@gmail.com'

# Configure itsdangerous
app.config['SECRET_KEY'] = 'demoapp'
mail=Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'target_db'
}
def send_reset_email(email, reset_url):
    subject = 'Password Reset Request'
    body = render_template('reset_email.html', reset_url=reset_url)

    message = Message(subject, recipients=[email], html=body)
    mail.send(message)


def connect_to_db():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        email = request.form['email']

        # Check if the email exists in the database
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            # Generate a unique token
            token = serializer.dumps(email, salt='change-password')

            # Send email with the reset link
            reset_url = url_for('reset_token', token=token, _external=True)
            send_reset_email(email, reset_url)

            flash('An email with instructions to reset your password has been sent.', 'info')
            return redirect(url_for('index'))
        else:
            flash('Email not found in the database.', 'danger')

    return render_template('change_password.html')

@app.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    try:
        email = serializer.loads(token, salt='change-password', max_age=10800)  # Token valid for 3 hours
    except:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password == confirm_password:
            # Update the password in the database
            connection = connect_to_db()
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET password=%s WHERE email=%s", (new_password, email))
            connection.commit()
            cursor.close()

            flash('Your password has been successfully updated.', 'success')
            return redirect(url_for('index'))
        else:
            flash('New password and confirm password do not match.', 'danger')

    return render_template('new_password.html', email=email)


if __name__=="__main__":
    app.run(debug=True,port=5001)