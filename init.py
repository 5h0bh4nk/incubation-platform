from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient

import bcrypt
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = 'mysecret'
socketio = SocketIO(app)

client = MongoClient('mongodb+srv://shubh4nk:h3ermOzKU1XQ2dJv@cluster0.s7x0c.mongodb.net/test')
db = client.Users


# index route
@app.route("/")
def index():
    if 'username' in session:
        return render_template("index.html", user=session['username'])
    return render_template("index.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        users = db.Users
        login_user = users.find_one({'name' : request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['pw']) == login_user['pw']:
                session['username'] = request.form['username']
                return redirect(url_for('index'))

        return 'Invalid username/password combination'
    return render_template("login.html")

@app.route("/convos", methods=["GET"])
def convos():
    if session['username']:
        user = session['username']
        return render_template("convos.html", user=user)
    return redirect(url_for('login'))

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':

        if not request.form.get("username"):
            return "Please provide a username!"
        elif not request.form.get("password"):
            return "Please provide a password!"
        elif not request.form.get("confirmation"):
            return "Please confirm your password!"
        
        username = request.form.get("username")
        password = request.form.get("password")
        
        users = db.Users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:

            if password != request.form.get("confirmation"):
                return 'Password doesn\'t match confirmation!'

            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'pw' : hashpass, 'preferences' : request.form.getlist('options')})
            session['username'] = username
            return redirect(url_for('index'))
    
        return 'That username already exists!'

    else:
        return render_template("signup.html")

@app.route("/inspiration", methods=["GET"])
def inspiration():
    return render_template("inspo.html", user=session["username"])

@app.route("/funding", methods=["GET"])
def funding():
    return render_template("funding.html", user=session["username"])

@app.route("/feedback") 
def feedback():
    return render_template("feedback.html")

@app.route("/logout", methods=["GET"])
def logout():
    session['username'] = ""
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
