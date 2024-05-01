#importing Necessary Libraries
import base64
import bcrypt
import io
import numpy as np
import pickle
import random
import re
import requests
import string
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, join_room, leave_room, send
from keras.preprocessing import image
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.models import load_model
from werkzeug.security import generate_password_hash, check_password_hash
from string import ascii_uppercase





app = Flask(__name__)

app.config["SECRET_KEY"] = "agri123"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'agritest'



mysql = MySQL(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login' 





app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/agritest'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class CropDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(255), nullable=False)
    date_planted = db.Column(db.Date)
    land_details = db.Column(db.Text)
    fertilizer_details = db.Column(db.Text)
    pesticides_details = db.Column(db.Text)
    other_details =db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('crop_details', lazy=True))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)

# Create tables
with app.app_context():
    db.create_all()
# Login route


@app.route('/')
def home():
    return render_template('home.html')


#====================================================DASHBOARD=================================================================================
#Backend code for Dashboard page

@login_manager.user_loader
def load_user(user_id):
    # Load and return the user from the database based on user_id
    return User.query.get(user_id)



@app.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        crop_details = CropDetail.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', crop_details=crop_details)
    else:
        return render_template('dashboard.html')
    

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_crop():
    if request.method == 'POST':
        crop_name = request.form['crop_name']
        date_planted = request.form['date_planted']
        land_details = request.form['land_details']
        fertilizer_details = request.form['fertilizer_details']
        pesticides_details = request.form['pesticides_details']
        other_details = request.form['other_details']

        new_crop = CropDetail(crop_name=crop_name, date_planted=date_planted,
                              land_details=land_details, fertilizer_details=fertilizer_details,
                              pesticides_details=pesticides_details, other_details=other_details,user=current_user)
        db.session.add(new_crop)
        db.session.commit()
        flash('Crop details added successfully!', category='success')
        return redirect(url_for('dashboard'))
    return render_template('add_crop.html')
    
@app.route('/crop/<int:crop_id>', methods=['GET', 'POST'])
@login_required
def crop_detail(crop_id):
    crop = CropDetail.query.get_or_404(crop_id)
    if crop.user != current_user:
        abort(403)  # Forbidden if trying to access crop details not belonging to the current user
    if request.method == 'POST':
        if request.form['action'] == 'delete':
            db.session.delete(crop)
            db.session.commit()
            flash('Crop details deleted successfully!', category='success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard page after deleting
        elif request.form['action'] == 'update':
            crop.crop_name = request.form['crop_name']
            crop.date_planted = request.form['date_planted']
            crop.land_details = request.form['land_details']
            crop.fertilizer_details = request.form['fertilizer_details']
            crop.pesticides_details = request.form['pesticides_details']
            crop.other_details = request.form['other_details']
            db.session.commit()
            flash('Crop details updated successfully!', category='success')
            return redirect(url_for('dashboard'))  # Redirect to the dashboard page after updating
    return render_template('crop_detail.html', crop=crop)

#===================================================SERVICES==================================================================================
#Backend code for Services page
@app.route('/services')
def services():
    return render_template('services.html' , is_services_page = True)

#---------------------------------------------------------------CROP RECOMMENDATION-----------------------------------------------------------------------------
#Loading Crop Recommendation Models
@app.route('/crop_recommendation')
def crop_recommendation():
    
    return render_template('crop_recommendation.html')


def display_image(cropname, table_name):
    cursor = mysql.connection.cursor()
    cursor.execute(f"SELECT image_data,image_url FROM {table_name} WHERE image_name = %s", (cropname,)) # Assuming id is the primary key of the image you want to display
    row= cursor.fetchone()

    if row:
        image_data = row[0]
        image_url = row[1]
    else:
        image_data = None
        image_url = None
    
      # Retrieve the image data
    cursor.close()

    # Convert image data to base64 encoding
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    return image_base64, image_url

minmaxpath = 'models/minmax_scaler.pkl'
with open(minmaxpath, 'rb') as file:
    scaler = pickle.load(file)

    # Loading the Random Forest Model 
with open('models/crop_recommendation.pkl', 'rb') as file:
    crop_model = pickle.load(file)
@app.route('/crop_name', methods=['POST'])
def crop_name():
    #loading pickles
    # Loading Scaler


    nitrogen =float(request.form['nitrogen'])
    phosphorus= float(request.form['phosphorus'])
    potassium = float(request.form['potassium'])
    temperature  = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    ph = float(request.form['ph'])
    rainfall = float(request.form['rainfall'])



    input_data  =[nitrogen,phosphorus,potassium,temperature,humidity,ph,rainfall]
    
    #Normalizing the data using the loaded Scaler
    normalized_input_data = scaler.transform([input_data])

    prediction = crop_model.predict(normalized_input_data)
    myprediction = prediction[0]

    image_data, image_url = display_image(myprediction, "crop_images")




    # print("Predicted Fertilizer: "+predicted_fertilizer[0])
    return render_template('crop_recommendation_result.html', myprediction=myprediction, image_data=image_data, image_url=image_url)

#-----------------------------------------------------------------DISEASE IDENTIFICATION---------------------------------------------------------------------------
disease_names = ['Apple___Apple_scab',
                   'Apple___Black_rot',
                   'Apple___Cedar_apple_rust',
                   'Apple___healthy',
                   'Blueberry___healthy',
                   'Cherry_(including_sour)___Powdery_mildew',
                   'Cherry_(including_sour)___healthy',
                   'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                   'Corn_(maize)___Common_rust_',
                   'Corn_(maize)___Northern_Leaf_Blight',
                   'Corn_(maize)___healthy',
                   'Grape___Black_rot',
                   'Grape___Esca_(Black_Measles)',
                   'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                   'Grape___healthy',
                   'Orange___Haunglongbing_(Citrus_greening)',
                   'Peach___Bacterial_spot',
                   'Peach___healthy',
                   'Pepper,_bell___Bacterial_spot',
                   'Pepper,_bell___healthy',
                   'Potato___Early_blight',
                   'Potato___Late_blight',
                   'Potato___healthy',
                   'Raspberry___healthy',
                   'Soybean___healthy',
                   'Squash___Powdery_mildew',
                   'Strawberry___Leaf_scorch',
                   'Strawberry___healthy',
                   'Tomato___Bacterial_spot',
                   'Tomato___Early_blight',
                   'Tomato___Late_blight',
                   'Tomato___Leaf_Mold',
                   'Tomato___Septoria_leaf_spot',
                   'Tomato___Spider_mites Two-spotted_spider_mite',
                   'Tomato___Target_Spot',
                   'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                   'Tomato___Tomato_mosaic_virus',
                   'Tomato___healthy']
disease_identification_model_path  = "models/disease_identification.h5"

disease_identification_model = load_model(disease_identification_model_path)


@app.route('/disease_name', methods=['POST'])
def disease_name():
    file = request.files['file']
    
    # Convert file storage object to bytes stream
    img_bytes = io.BytesIO(file.read())
    
    # Load image from bytes stream
    img = image.load_img(img_bytes, target_size=(100, 100))
    
    # Convert the image to an array
    img_array = image.img_to_array(img)
    
    # Expand the dimensions to match the shape expected by the model
    img_array = np.expand_dims(img_array, axis=0)
    
    # Normalize the pixel values
    img_array /= 255.
    
    # Make predictions using the loaded model
    predictions = disease_identification_model.predict(img_array)
    
    # Get the predicted class index
    predicted_class_index = np.argmax(predictions)
    
    # Map the predicted class index to the corresponding class label
    predicted_class_label = disease_names[predicted_class_index]
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT disease_name, disease_cause,chemical_methods,natural_methods FROM disease_details WHERE diseases = %s", (predicted_class_label,))
    disease_info = cursor.fetchone()
    disease_name = disease_info[0]
    disease_cause = disease_info[1].split('\n')
    chemical_methods = disease_info[2].split('\n')
    natural_methods = disease_info[3].split('\n')
    return render_template('disease_identification_result.html', predicted_class_label=predicted_class_label, disease_name = disease_name, disease_cause=disease_cause, chemical_methods = chemical_methods, natural_methods=natural_methods)




@app.route('/disease_identification')
def  disease_identification():
    return render_template('disease_identification.html')

#------------------------------------------------------------------FETILIZER RECOMMENDATION--------------------------------------------------------------------------

@app.route('/fertilizer_recommendation')
def fertilizer_recommendation():
    return render_template('fertilizer_recommendation.html')

with open('models/standard_scaler.pkl', 'rb') as file:
    standard_scaler = pickle.load(file)

    # Loading the Random Forest Model
with open('models/fertilizer_recommendation.pkl', 'rb') as file:
    fertilizer_model = pickle.load(file)

@app.route('/fertilizer_name', methods = ['POST'])
def fertilizer_name():
    #FUNCTION to convert categorical values of input_data to numerical values
    def catergorical_to_num(input_data):
        numerical_values = input_data

        # Load the label encoders for Soil_Type and Crop_Type
        soil_type_encoder = LabelEncoder()
        soil_type_encoder.classes_ = np.array(['Black', 'Clayey', 'Loamy', 'Red', 'Sandy'])

        crop_type_encoder = LabelEncoder()
        crop_type_encoder.classes_ = np.array(['Barley', 'Cotton', 'Ground Nuts', 'Maize', 'Millets', 'Oil seeds', 'Paddy', 'Pulses', 'Sugarcane', 'Tobacco', 'Wheat'])

        # Encode the categorical values
        soil_type_encoded = soil_type_encoder.transform([input_data[3]])[0]
        crop_type_encoded = crop_type_encoder.transform([input_data[4]])[0]

        # Combine numerical and encoded values
        encoded_data = input_data[:3] + [soil_type_encoded, crop_type_encoded] + list(map(int, input_data[-3:]))
        return encoded_data
    


    #get the input values from the form
    input_data=[]
    input_data.append(float(request.form['Temperature']))
    input_data.append(float(request.form['Humidity']))
    input_data.append(float(request.form['Moisture']))
    input_data.append(request.form['Soil Type'])
    input_data.append(request.form['Crop Type'])
    input_data.append(float(request.form['Nitrogen']))
    input_data.append(float(request.form['Potassium']))
    input_data.append(float(request.form['Phosphorous']))

    new_data = [catergorical_to_num(input_data)]
    # Applying Standar_Scaling to new data
    scaled_data = standard_scaler.transform(new_data)  # Use transform, not fit_transform

    # Predicting for new value with the loaded model
    prediction = fertilizer_model.predict(scaled_data)



    # Reversing dictionary of label encodings

    reverse_fertilizer = {0: '10-26-26', 1: '14-35-14', 2: '17-17-17', 3: '20-20', 4: '28-28', 5: 'DAP', 6: 'Urea'}
    predicted_fertilizer = [reverse_fertilizer[prediction[0]]]

    image_data, image_url = display_image(predicted_fertilizer, "fertilizer_images")

    # print("Predicted Fertilizer: "+predicted_fertilizer[0])
    return render_template('fertilizer_recommendation_result.html', recommended=predicted_fertilizer[0], image_data=image_data, image_url=image_url)
#---------------------------------------------------------------------CHECK WEATHER-----------------------------------------------------------------------
@app.route('/check_weather')
def check_weather():
    return render_template('check_weather.html')

#==============================================================NEWS=======================================================================
#Backend code for News page
@app.route('/news')
def news():
    return render_template('news.html')

#==============================================================CONNECT=======================================================================
#Backend code for Connect page
socketio = SocketIO(app)
connect_rooms = {}
def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in connect_rooms:
            break
    
    return code


@app.route("/connect_home", methods=["POST", "GET"])
def connect_home():
    session.clear()
    room_codes = connect_rooms.keys()  # Extract room codes from the dictionary
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("connect_home.html", error="Please enter a name.", code=code, name=name, room_codes=room_codes)

        if join != False and not code:
            return render_template("connect_home.html", error="Please enter a room code.", code=code, name=name, room_codes=room_codes)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            connect_rooms[room] = {"members": 0, "messages": []}
        elif code not in connect_rooms:
            return render_template("connect_home.html", error="Room does not exist.", code=code, name=name, room_codes=room_codes)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("connect_room"))

    return render_template("connect_home.html", room_codes=room_codes)


@app.route("/connect_room")
def connect_room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in connect_rooms:
        return redirect(url_for("connect_home"))

    return render_template("connect_room.html", code=room, messages=connect_rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in connect_rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    connect_rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in connect_rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    connect_rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in connect_rooms:
        connect_rooms[room]["members"] -= 1
        if connect_rooms[room]["members"] <= 0:
            del connect_rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


#==============================================================LOGIN SIGNUP=======================================================================
#Backend code for Login page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email:  # Check if email is empty
            flash('Please enter your email.', category='error')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Register route
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())
            new_user = User(email=email, first_name=first_name, password=hashed_password.decode('utf-8'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('home'))
    
    return render_template("sign_up.html", user=current_user)




#========================================================Footer======================================================

@app.route('/contact')

def contact():
    return render_template('contact.html')


@app.route('/feedback')

def feedback():
    return render_template('feedback.html')
    


if __name__ == '__main__':
    socketio.run(app, debug=True)
