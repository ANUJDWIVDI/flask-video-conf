from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
import random
import string
import io
import xlsxwriter
from datetime import datetime
import pytz
import uuid
import os
import requests
from werkzeug.utils import secure_filename
from bson import ObjectId

# Initialize Flask application
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://anuj:penguin123@cluster0.qktfwxj.mongodb.net/video_conf_app?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '79bc76001@smtp-brevo.com'
app.config['MAIL_PASSWORD'] = 'Br9PdzXWwMVQabp1'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

mongo = PyMongo(app)
mail = Mail(app)

@app.shell_context_processor
def make_shell_context():
    return dict(mongo=mongo)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return render_template('dashboard.html', user=user)
    else:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        registration_date = datetime.now(pytz.utc)
        department = request.form['department']
        semester = request.form['semester']
        phone_number = request.form['phone_number']

        user = {
            'email': email,
            'password': password,  # Store plaintext password
            'full_name': full_name,
            'registration_date': registration_date,
            'department': department,
            'semester': semester,
            'phone_number': phone_number,
            'profile_picture': None
        }

        try:
            mongo.db.users.insert_one(user)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})

        if user and user['password'] == password:  # Compare plaintext passwords
            session['user_id'] = str(user['_id'])  # Convert ObjectId to string for the session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/create_meeting', methods=['POST'])
def create_meeting():
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    if not profile_complete(user):
        flash('Please complete your profile before creating a meeting.', 'warning')
        return redirect(url_for('dashboard'))

    room_name = generate_meeting_code()  # Generate a unique room name
    invitees = request.form['invitees']
    meeting_link = url_for('join_meeting', _external=True) + '?room=' + room_name
    
    meeting = {
        'host_id': session['user_id'],
        'room_name': room_name,
        'invitees': invitees.split(',')
    }
    mongo.db.meetings.insert_one(meeting)
    send_invites(invitees, room_name)  # Function to send invites
    
    return render_template('dashboard.html', user=user, meeting_link=meeting_link)


@app.route('/test')
def test():
    return redirect("https://2d44a1400ceb8c0dacdc.vercel.app/")

@app.route('/join_meeting', methods=['GET'])
def join_meeting():
    room_name = request.args.get('room')
    user_name = request.args.get('name')
    
    if not room_name:
        flash('Meeting code is required.', 'danger')
        return redirect(url_for('dashboard'))

    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if user:
        return render_template('video_call.html', room_name=room_name, user_name=user_name)
    
    flash('You need to log in first.', 'warning')
    return redirect(url_for('login'))

def generate_meeting_code():
    return str(uuid.uuid4()).split('-')[0]  # Example code generation

def send_invites(invitees, room_name):
    # Implement email sending functionality here
    pass

def profile_complete(user):
    required_fields = ['full_name', 'department', 'semester', 'phone_number']
    return all(user.get(field) for field in required_fields)

@app.route('/attendance_report/<meeting_id>')
def attendance_report(meeting_id):
    attendance = mongo.db.attendance.find({'meeting_id': meeting_id})
    data = [['User', 'Status']]
    for record in attendance:
        user = mongo.db.users.find_one({'_id': record['user_id']})
        data.append([user['full_name'], record['status']])
    return generate_excel(data)

def generate_excel(data):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    for row_num, row_data in enumerate(data):
        for col_num, col_data in enumerate(row_data):
            worksheet.write(row_num, col_num, col_data)
    workbook.close()
    output.seek(0)
    return send_file(output, attachment_filename='attendance_report.xlsx', as_attachment=True)

@app.route('/send_message', methods=['POST'])
def send_message():
    meeting_id = request.form['meeting_id']
    message = request.form['message']
    chat = {
        'meeting_id': meeting_id,
        'user_id': session.get('user_id'),
        'message': message,
        'timestamp': datetime.now(pytz.utc)
    }
    mongo.db.chats.insert_one(chat)
    return redirect(url_for('meeting', meeting_id=meeting_id))

@app.route('/check-email', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email')
    
    if email:
        user = mongo.db.users.find_one({'email': email})
        if user:
            return jsonify({'exists': True}), 200
        else:
            return jsonify({'exists': False}), 200
    return jsonify({'error': 'No email provided'}), 400

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = mongo.db.users.find_one({'email': email})
        if user:
            token = generate_reset_token(user)
            if send_reset_email(user['email'], token):
                flash('Password reset email sent!', 'success')
                print('Password reset email sent successfully.')
            else:
                flash('Failed to send password reset email. Please try again later.', 'danger')
                print('Failed to send password reset email.')
        else:
            flash('Email not found.', 'danger')
            print('Email not found for password reset.')
    return render_template('reset_password.html')

def send_reset_email(email, token):
    try:
        msg = Message('Password Reset Request', sender='your_email@example.com', recipients=[email])
        msg.body = f'To reset your password, visit the following link: {url_for("reset_password_token", token=token, _external=True)}'
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

import secrets

def generate_reset_token(user):
    token = secrets.token_urlsafe(32)  # Generate a secure random token
    mongo.db.users.update_one({'_id': user['_id']}, {'$set': {'reset_token': token}})
    return token

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password == confirm_password:
            user = mongo.db.users.find_one({'reset_token': token})
            if user:
                mongo.db.users.update_one({'reset_token': token}, {'$set': {'password': password, 'reset_token': None}})
                flash('Password reset successfully!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid or expired token.', 'danger')
        else:
            flash('Passwords do not match.', 'danger')
    return render_template('reset_password_token.html', token=token)

@app.route('/screen_share')
def screen_share():
    return render_template('screen_share.html')

@app.route('/upload_meeting_notes', methods=['POST'])
def upload_meeting_notes():
    if 'notes' in request.files:
        notes = request.files['notes']
        # Handle the uploaded notes file here (save or process it)
        flash('Meeting notes uploaded successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))
    file = request.files['profile_picture']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        user_id = session.get('user_id')
        if user_id:
            mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'profile_picture': filename}})
            flash('Profile picture uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

if __name__ == '__main__':
    app.run(debug=True)
