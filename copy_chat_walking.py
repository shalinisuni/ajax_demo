from flask import Flask, render_template, redirect,session,request,url_for,jsonify,flash
import hashlib
import smtplib, ssl
from flask_mail import Mail, Message
from random import *
import re
import mysql.connector
from datetime import datetime

app = Flask(__name__)
mail=Mail(app)
app.secret_key="target"


# app.config['MAIL_SERVER']='smtp.gmail.com'
# app.config['SECRET_KEY'] = 'target'
# app.config['MAIL_PORT']=465
# app.config['MAIL_USERNAME']="shalini18031999@gmail.com"
# app.config['MAIL_PASSWORD']="glba witq lcvy bkom"
# app.config['MAIL_USE_TLS']=False
# app.config['MAIL_USE_SSL']=True

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'target_db'
}


def connect_to_db():
    return mysql.connector.connect(**db_config)

@app.route('/logout')
def logout():
    session.pop('email',None)
    return render_template('index.html')

@app.route('/cancel')
def cancel():
     session.pop('email',None)
     return render_template('index.html')

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password = hashlib.md5(password.encode()).hexdigest()
        user_id = get_user_id(email, password)
        print(user_id)
        if user_id is not None:
            session['user_id'] = user_id
            return redirect(url_for('target'))
        else:
            flash("Invalid email or password",'error')
            return render_template('index.html')
    return render_template('index.html', msg='Invalid email or password')

    
# Function to get user ID based on email and password
def get_user_id(email, password):
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT user_id FROM users WHERE email = %s AND password = %s', (email, password))
    user = cursor.fetchone()
    print(user)
    connection.close()
    return user['user_id'] if user else None

# Function to fetch target data based on user ID and target name
def get_target_data(user_id, target_name):
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT total_target_count, cumulative_target FROM target WHERE user_id = %s AND target_name = %s', (user_id, target_name))
    target_data = cursor.fetchone()
    #print(target_data)
    connection.close()
    return target_data

@app.route('/register',methods=['Get','Post'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmpass']
        if not name.isalpha():
            return "Name should contain only alphabets."
        if not phone.isdigit() and re.match(r'^\d{10}$', phone) :
            return "Phone number should contain only 10 digits."
        # if not re.match(r'^[a-zA-Z]+@[a-zA-Z]+\.[a-zA-Z]+$', email) :
        #     return "email Id is not valid please check"
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (name, phone, email, password) VALUES (%s, %s, %s, %s)',(name, phone, email, hashed_password))
        connection.commit()
        cursor.close()
        flash("registered Sucessfully")
        return render_template("index.html")

    return render_template('register.html')

@app.route('/target', methods=['GET'])
def target_page():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']

    # Fetch target names for the dropdown
    connection = connect_to_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT  target_name FROM target WHERE user_id = %s', (user_id,))
    target_names = [row['target_name'] for row in cursor.fetchall()]
    print(target_names)
    print("this is target_name")
    cursor.execute("select name from users where user_id=%s",(user_id,))
    uname=[r['name'] for r in cursor.fetchall()]
   
    print(str(uname))
    
    return render_template('target.html', target_names=target_names,uname=uname)

# Ajax route to fetch target details
@app.route('/get_target_details', methods=['POST'])
def get_target_details():
    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({'error': 'User not authenticated'})

    target_name = request.json['target_name']
    target_data = get_target_data(user_id, target_name)
    return jsonify(target_data)

@app.route('/history',methods=['Get'])
def history():
    if 'user_id' not in session:
        return redirect(url_for('index'))
     
    connection = connect_to_db()
    cursor=connection.cursor()
    cursor.execute("SELECT target_name, count, DATE_FORMAT(date,'%d-%m-%Y %H:%i') from transactions")
    res=cursor.fetchall()
    cursor.close()
    print(res)
    new_data=res 
    return render_template("history.html",new_data=new_data)
   

@app.route('/submit',methods=['GET','Post'])
def submit():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user_id = session['user_id']
    targetDropdown=request.form['targetDropdown']
    todayCount=int(request.form['todayCount'])
    print(todayCount,targetDropdown)
    target_data = get_target_data(user_id, targetDropdown)
    total_target=target_data['total_target_count']
    cumulative=target_data['cumulative_target']
    print(type(total_target))
    if total_target > todayCount:
        connection = connect_to_db()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO transactions (target_name,count) VALUES (%s, %s)',(targetDropdown,todayCount))
        connection.commit()
        target_data = get_target_data(user_id, targetDropdown)
        cumulative=target_data['cumulative_target']
        cursor.execute(f"update target set cumulative_target={cumulative} + {todayCount} where user_id='%s' and target_name=%s",(user_id,targetDropdown))
        print(f"{todayCount} and {cumulative}")
        connection.commit()
        cursor.close()
        return render_template("target.html", msg=f"today count {todayCount} {targetDropdown} is added into the database suceessfully ")
    else:
        return redirect(url_for('target_page' , msg="today count is greater than total target count please enter the correct value"))

def send_email(message):
    host = "smtp.gmail.com" 
    port = 465

    username = "shalini18031999@gmail.com"
    password = "glba witq lcvy bkom"

    receiver = "shalini18031999@gmail.com"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)


@app.route('/change_password',methods=['Get','Post'])
def change_password():
    if request.method == 'POST':    
        email=request.form['email']
        connection = connect_to_db()
        cursor=connection.cursor()
        cursor.execute("SELECT email from users")
        res=cursor.fetchall()
        for i in res:
            print(list(i))
        cursor.close()
        # if email in i:
        
        gotp=generate_otp()
        print(f"otp number is {gotp}")
        # msg = Message('OTP Validation', sender='shalini18031999@gamil.com', recipients=[email])
        # msg.body=f'Your OTP is: {otp}'
        # mail.send(msg)
        send_email(message=f"OTP is {gotp}")
        flash("OTP has sent to your mail ID")
        return render_template("otp_email.html")
    return render_template("change_password.html")

def generate_otp():
    otp=randint(0000,9999)
    print(otp)
    return otp


@app.route('/otp',methods=['Get','Post'])
def otp():
    if request.method == 'POST': 
        user_otp=request.form['otp']
        gotp=generate_otp
        g=int(gotp)
        u=int(user_otp)
        print(type(g))
        print(type(u))
        if gotp==int(user_otp):
            flash("Email verified successfully")
            return render_template("new_password.html")
    return render_template("change_password.html")

        

if __name__=="__main__":
    app.run(debug=True,port=5002)