from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'agritest'

mysql = MySQL(app)

# Read the image file
def read_image(file_path):
    with open(file_path, "rb") as file:
        return file.read()

# Upload images and names into the database
# Upload images, names, and URLs into the database
def upload_image(image_data, image_name, image_url):
    with app.app_context():
        cursor = mysql.connection.cursor()
        query = "INSERT INTO fertilizer_images (image_data, image_name, image_url) VALUES (%s, %s, %s)"
        cursor.execute(query, (image_data, image_name, image_url))
        mysql.connection.commit()
        cursor.close()

# Example usage
folder_path = "static/images/fertilizer_images"  # Path to the folder containing images
for filename in os.listdir(folder_path):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        image_path = os.path.join(folder_path, filename)
        image_name = os.path.splitext(filename)[0]
        image_url = "https://www.coromandel.biz/product-service/gromor-" + image_name 
        image_data = read_image(image_path)
        upload_image(image_data, image_name, image_url)
