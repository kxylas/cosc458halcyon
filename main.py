from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
users = {}
peer_groups = {}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this feature.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username and password:
            if username not in users:
                users[username] = {
                    'password': generate_password_hash(password),
                    'moods': []
                }
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Username already exists. Please choose another.', 'danger')
        else:
            flash('Invalid registration data. Please try again.', 'danger')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        mood = request.form['mood']
        users[session['username']]['moods'].append(mood)
        flash('Mood logged successfully!', 'success')
    return render_template('dashboard.html', moods=users[session['username']]['moods'])


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/schedule_teletherapy', methods=['POST'])
@login_required
def schedule_teletherapy():
    date = request.form.get('date')
    time = request.form.get('time')
    duration = request.form.get('duration')
    print(f'Date: {date}, Time: {time}, Duration: {duration} minutes')
    return 'Teletherapy scheduled successfully'


@app.route('/track_mood', methods=['POST'])
@login_required
def track_mood():
    mood = request.form.get('mood')
    notes = request.form.get('notes')
    print(f'Mood: {mood}, Notes: {notes}')
    return 'Mood tracked successfully'


@app.route('/crisis_response', methods=['GET'])
@login_required
def crisis_response():
    return render_template('crisis_response.html')


@app.route('/feedback', methods=['POST'])
@login_required
def feedback():
    data = request.json
    feedback_message = data.get('message')
    print(f"Feedback from {session['username']}: {feedback_message}")
    return jsonify({'message': 'Feedback received successfully'})


@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        if group_name:
            peer_groups[group_name] = {
                'members': [session['username']],
                'messages': []
            }
            flash(f'Group "{group_name}" created successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid group name. Please try again.', 'danger')

    return render_template('create_group.html')


@app.route('/join_group', methods=['GET', 'POST'])
@login_required
def join_group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        if group_name in peer_groups:
            peer_groups[group_name]['members'].append(session['username'])
            flash(f'Joined group "{group_name}" successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Group not found. Please try again.', 'danger')
    return render_template('join_group.html')


@app.route('/peer_group_chat', methods=['GET', 'POST'])
@login_required
def peer_group_chat():
    group_name = request.args.get('group_name')
    if group_name in peer_groups and session['username'] in peer_groups[group_name]['members']:
        if request.method == 'POST':
            message = request.form['message']
            if message:
                peer_groups[group_name]['messages'].append({
                    'user': session['username'],
                    'message': message
                })
            else:
                flash('Empty messages are not allowed.', 'danger')
        return render_template('peer_group_chat.html',
                               group_name=group_name,
                               messages=peer_groups[group_name]['messages'])
    else:
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/mental_health_activities')
@login_required
def mental_health_activities():
    return render_template('mental_health_activities.html')


if __name__ == '__main__':
    app.run(debug=True)

