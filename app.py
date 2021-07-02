from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import helper

app = Flask(__name__)

app.secret_key='deepansh'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pahwadeepansh11'
app.config['MYSQL_DB'] = 'blog'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password))
        account = cursor.fetchone()
        if account['Roles'] == "User":
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['Roles'] = account['Roles']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        elif account['Roles'] == "Admin":
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['Roles'] = account['Roles']
            msg = 'Logged in successfully !'
            return render_template('admin.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('Roles', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_id = helper.id()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute("INSERT INTO accounts VALUES (% s , % s, % s, % s,'User')", (user_id,username, password, email,Roles ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route("/notifications")
def notifications():
    if 'loggedin' in session:
        return render_template("notifications.html")
    return redirect(url_for('login'))

@app.route("/create",methods =['GET', 'POST'])
def create():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'create_notification' in request.form:
                notifications = request.form['create_notification']
                post_id = helper.id()
                cursor.execute("INSERT INTO posts VALUES (% s, % s, % s)", (session['id'],notifications,post_id))
                mysql.connection.commit()
    return render_template('create.html',msg="Post Created")

@app.route("/update",methods =['GET', 'POST'])
def update():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'update_notification' in request.form and 'post_id' in request.form:
                notifications = request.form['update_notification']
                post_id = request.form['post_id']
                id = session['id']
                cursor.execute("UPDATE posts SET notification = % s WHERE post_id = % s AND id = % s", (notifications,post_id,id))
                mysql.connection.commit()
        elif not re.match(r'[A-Za-z0-9]+', notifications):
            msg = "Please enter valid input"
        elif not re.match(r'[0-9]+', post_id):
            msg = "Please enter valid input"
        else:
            msg="Please enter your authorized post id"
    return render_template('update.html',msg="Post Updated")

@app.route("/view")
def view():
    if 'loggedin' in session and session['Roles'] == "Admin" :
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * from posts")
        output_data=cursor.fetchall()
        return render_template("view.html",data=output_data)
        cursor.close()
    elif 'loggedin' in session:
        cursor = mysql.connection.cursor()
        id = session['id']
        cursor.execute("SELECT * from posts where id= % s",[id])
        output_data=cursor.fetchall()
        return render_template("view.html",data=output_data)
        cursor.close()


@app.route("/delete",methods =['GET', 'POST'])
def delete():
    if 'loggedin' in session and session['Roles'] == "Admin":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'post_id' in request.form:
            post_id = request.form['post_id']
            cursor.execute("DELETE FROM posts where post_id = % s",(post_id))
            mysql.connection.commit()
    elif 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'post_id' in request.form:
            post_id = request.form['post_id']
            id = session['id']
            cursor.execute("DELETE FROM posts where post_id = % s AND id=%s",(post_id,id))
            mysql.connection.commit()
    return render_template('delete.html',msg="Successfully deleted the post")

if __name__ == '__main__':
    app.run()
