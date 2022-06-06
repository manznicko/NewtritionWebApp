# Insert API logic
#Everything we need to import
from sqlalchemy.sql.expression import false, true
from flask import Flask, render_template, request, flash, jsonify, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, login_required, logout_user, UserMixin, LoginManager
from sqlalchemy import create_engine, delete, ForeignKey
from sqlalchemy.orm import backref, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import pandas as pd 
import json

# from typing import Dict
# from pandas.core.frame import DataFrame
# import requests


#app, login_manager, admin, db initialization
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config['SECRET_KEY'] = "super secret"
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.secret_key = "super secret"
login_manager = LoginManager(app) 
login_manager.init_app(app) 
login_manager.login_view = 'login'
# cnx = create_engine('sqlite:///user.sqlite3').connect()
db = SQLAlchemy(app)
admin = Admin(app, name='microblog', template_mode='bootstrap3')

class user(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.email = email

    def check_password(self, password):  #RETURNS A BOOLEAN, TRUE OR FALSE
        return check_password_hash(self.password_hash, password)

class FoodRecords(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.String(100), unique=True, nullable=False)
    calories = db.Column(db.Integer, unique=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('user', backref=db.backref('FoodRecords', lazy=True))

    def __init__(self, date, calories, user_id):
        self.date = date
        self.calories = calories
        self.user_id = user_id

class userStats(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    heightFeet = db.Column(db.Integer, unique=False, nullable=True)
    heightInches = db.Column(db.Float, unique=False, nullable=True)
    weight = db.Column(db.Float, unique=False, nullable=True)
    date = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('user', backref=db.backref('userStats', lazy=True))

    def __intit__(self, heightFeet, heightInches, weight, date, user_id):
        self.heightFeet = heightFeet
        self.heightInches = heightInches
        self.weight = weight
        self.date = date
        self.user_id = user_id


class adminPriv(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('user', backref=db.backref('adminPriv', lazy=True))

#ADDING MODEL VIEWS TO ADMIN
admin.add_view(ModelView(user, db.session)) 
admin.add_view(ModelView(adminPriv, db.session)) 
admin.add_view(ModelView(FoodRecords, db.session))
admin.add_view(ModelView(userStats, db.session))


#START OF ALL other functions



# START OF ALL @app.route() functions 
@login_manager.user_loader 
def load_user(userid): 
    return user.query.get(userid)

@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    msg = ''
    if current_user.is_authenticated:
        return redirect(url_for('My_Dashboard'))
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        userN = request.form['username']
        passW = request.form['password']
        User = user.query.filter_by(username=userN).first()
        # print(User.username)
        # print(userN +' ' + passW)

        if (User is None) or (User.check_password(passW) is false):
            flash("Either username or password were incorrect")
            msg = "Username or password were incorrect"
            # return redirect(url_for('login'), msg = msg)
        elif(User.check_password(passW)):
            login_user(User)
            return(redirect(url_for('My_Dashboard')))
            
        
    return(render_template('login.html', msg= msg))

@app.route('/stats', methods = ['POST'])
def stats():
    User = current_user
    if(request.method == 'POST'):
        stats = request.form['heightF'] 
        # print(stats)
        date = datetime.now()
        # print('test')
        
        # stats_new = userStats(heightFeet= stats['heightF'], heightInches= stats['heightI'], weight=stats['weight'], date= date.strftime("%d/%m/%y"), user_id = User.id)
        # db.session.add(stats_new)
        # db.commit()
    return()


    

@app.route('/index')
@login_required
def index():
    msg = 'test'
    # print(current_user.username)
    User = user.query.filter_by(username = current_user.username)
    return render_template('index.html', user = User)

@app.route('/My_Dashboard')
@login_required
def My_Dashboard():
    user = current_user.username
    return render_template('My_Dashboard.html', user = user)

@app.route('/setting.html')
@login_required
def setting():
    # msg = 'test'
    # print(current_user.username)
    User = user.query.filter_by(username = current_user.username).first()
    # print(User.username)
    return render_template('setting.html', user = User.username, email = User.email)

@app.route('/records.html')
@login_required
def records():
    # msg = 'test'
    print(current_user.username)
    user = current_user.username
    return render_template('records.html', user = user)

@app.route('/posts.html', methods=['GET','POST'])
@login_required
def posts():
    User = current_user
    return render_template('posts.html', user = User.username)

@app.route('/My_Dashboard.html')
@login_required
def test1():
    # msg = 'test'
    # print(current_user.username)
    user = current_user.username
    return render_template('my_Dashboard.html', user = user)

@app.route('/socialmediapartner.html')
@login_required
def soc():
    return(render_template('socialmediapartner.html'))

@app.route('/profile.html', methods=['GET', 'POST'])
@login_required
def profile():
    User = current_user
    if(request.method == 'POST'):
        stats = request.form['heightF'] 
        print(stats)
        date = datetime.now()
        print('test')
        
        # stats_new = userStats(heightFeet= stats['heightF'], heightInches= stats['heightI'], weight=stats['weight'], date= date.strftime("%d/%m/%y"), user_id = User.id)
        # db.session.add(stats_new)
        # db.commit()
    return(render_template('profile.html', user = current_user.username))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form : 
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        print(username)
        User = user.query.filter_by(username=username).first()
        if (User is not None):
            msg = 'Account already exists'
        elif(User is None and (username != '' and password != '' and email!='')):
            registered_user = user(username = username, password = password, email = email)   
            db.session.add(registered_user)
            db.session.commit()
            msg = 'Succcessfully registered! You can now login. '
        else:
            msg = "Please fill out entire form!"
    elif(request.method == 'POST'):
        msg = "Please fill out the entire form!"
        return(render_template('register.html', msg=msg))

    return(render_template('register.html', msg = msg))

@app.route('/admin', methods = ['GET'])
@login_required
def adminView():
    User = current_user
    print('test')
    if(request.method == 'GET'):
        # User = current_user
        check = adminPriv.query.filter_by(user_id=current_user.get_id()).first()
        print(check)
        print("test")
        if(check is None or current_user.is_anonymous):
            return (render_template("index.html", user=User.username))
        else:
            return(redirect(url_for('admin')))
    return(render_template("index.html", user=User.username))

if __name__ == '__main__':
    db.create_all()
    app.run()
    #db.drop_all()