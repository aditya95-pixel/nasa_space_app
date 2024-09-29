# load packages==============================================================
from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import sklearn
import numpy as np
import sqlite3
from decouple import config
dtr=pickle.load(open('dtr.pkl','rb'))
preprocessor=pickle.load(open('preprocessor.pkl','rb'))
app = Flask(__name__)
app.secret_key = config("app.secret_key")
def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
    print("Table created successfully")
    conn.close()
init_sqlite_db()
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html',username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash("Invalid login credentials. Please try again.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            # Generate the password hash using the default method
            hashed_password = generate_password_hash(password)

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()

            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        else:
            flash("Passwords do not match. Please try again.")
            return redirect(url_for('register'))

    return render_template('register.html')
@app.route('/cropyield')
def cropyield():
    return render_template('cropyield.html')
@app.route("/predict",methods=['POST'])
def predict():
    if request.method == 'POST':
        Year = request.form['Year']
        average_rain_fall_mm_per_year = request.form['average_rain_fall_mm_per_year']
        pesticides_tonnes = request.form['pesticides_tonnes']
        avg_temp = request.form['avg_temp']
        Area = request.form['Area']
        Item  = request.form['Item']
        features = np.array([[Year,average_rain_fall_mm_per_year,pesticides_tonnes,avg_temp,Area,Item]],dtype=object)
        transformed_features = preprocessor.transform(features)
        prediction = dtr.predict(transformed_features).reshape(1,-1)
        return render_template('cropyield.html',prediction = prediction)
@app.route('/weather')
def weather():
    return render_template('weather.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/research')
def research():
    return render_template('research.html')
@app.route('/resources')
def resources():
    return render_template('resources.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)