# load packages==============================================================
from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import sklearn
import numpy as np
import sqlite3
from decouple import config
dtr=pickle.load(open('./Models/cropyield/dtr.pkl','rb'))
preprocessor=pickle.load(open('./Models/cropyield/preprocessor.pkl','rb'))
model1=pickle.load(open('./Models/croprecommender/model.pkl','rb'))
ms = pickle.load(open('./Models/croprecommender/minmaxscaler.pkl','rb'))
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
@app.route("/predict_yield",methods=['POST'])
def predict_yield():
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
        return render_template('cropyield.html',prediction = prediction[0][0])
@app.route('/croppredict')
def croppredict():
    return render_template("croppredict.html")

@app.route("/predict_crop",methods=['POST'])
def predict_crop():
    N = request.form['Nitrogen']
    P = request.form['Phosporus']
    K = request.form['Potassium']
    temp = request.form['Temperature']
    humidity = request.form['Humidity']
    ph = request.form['Ph']
    rainfall = request.form['Rainfall']

    feature_list = [N, P, K, temp, humidity, ph, rainfall]
    single_pred = np.array(feature_list).reshape(1, -1)

    scaled_features = ms.transform(single_pred)
    prediction = model1.predict(scaled_features)

    crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                 14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                 19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}

    if prediction[0][0] in crop_dict:
        crop = crop_dict[prediction[0][0]]
        result = "{} is the best crop to be cultivated right there".format(crop)
    else:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."
    return render_template('croppredict.html',result = result)
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
@app.route('/learnmore')
def learnmore():
    return render_template('learnmore.html')
@app.route('/soilWater')
def soilWater():
    return render_template('soilWater.html')
@app.route('/cropMonitoring')
def cropMonitoring():
    return render_template('cropMonitoring.html')
def soilWater():
    return render_template('soilWater.html')
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)