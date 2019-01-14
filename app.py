from flask import Flask, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_socketio import SocketIO
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////root/Desktop/metabase/database.db"
app.config['SECRET_KEY'] = "70NYS74RK"
db = SQLAlchemy(app)
socketio = SocketIO(app)

class User(db.Model):
    id = db.Column('id', db.Integer(), primary_key=True)
    username = db.Column('username', db.String(32), unique=True)
    password = db.Column('password', db.String(50))

class Messages(db.Model):
    id = db.Column('id', db.Integer(), primary_key=True)
    username = db.Column('username', db.String(32))
    text = db.Column('text', db.String(500))



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    try:
        if session['is_logged']:
            user = session['user']
            data = {'message' : user }
            socketio.emit('new_user', data)
            location = 'http://metabase.serveo.net/'
            return render_template('chat.html', username=user, location=location)
        else:
            return redirect('login')
    except KeyError:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':    
        username = request.form['Username']
        password = request.form['Password']
        validate = User.query.filter_by(username=username).first()
        if validate is not None:
            if password == validate.password:
                session['user'] = validate.username
                session['is_logged'] = True
                
                return redirect(url_for('chat'))
            else:
                socketio.emit('invalid_login')
                return render_template('login.html', retry=True)
        else:
            return render_template('login.html', retry=True)
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        data = User.query.filter_by(username=username).first()
        if data is None:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', retry=True)

@app.route('/logout')
def logout():
    try:
        if session['is_logged']:
            session['is_logged'] = False
            return render_template('login.html')
    except KeyError:
        return redirect(url_for('index'))

@socketio.on('user_exit')
def exit_user(msg):
    socketio.emit('exit_user', msg)

@app.route('/changemusic/<mid>')
def music(mid, method=['GET']):
    try:

        if session['user']:
            url = "http://youtuberepeater.com/watch?v="
            mid = url + str(mid)
            mid = {'message': mid}
            socketio.emit('changemusic', mid)
            return "<h1>Changed</h1>"
    except:
        return "<h1>Go n fcuk urself</h1>"

@socketio.on('message')
def message(msg):
    socketio.emit('message_action', msg)
    message = Messages(username=msg['username'], text=msg['message'])


if __name__ == "__main__":
   socketio.run(app)

