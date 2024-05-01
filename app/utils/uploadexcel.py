from flask import Flask, request
import pandas as pd
import MySQLdb

app = Flask(__name__)

# MySQL configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'agritest'

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file is present in the request
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']

    # Read the Excel file using pandas
    df = pd.read_excel(r"data\raw\plant_diseases_data\disease_preventionlist.xlsx")

    # Establish a connection to the MySQL database
    conn = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB)
    cursor = conn.cursor()

    # Iterate over the rows of the DataFrame and insert data into the MySQL table
    for index, row in df.iterrows():
        query = "INSERT INTO table_name (`disease_name`, `disease_cause`, `chemical_methods`, `natural_methods`, `diseases`) VALUES (%s, %s,%s, %s, %s)"
        values = (row['disease_name'], row['disease_cause'],row['chemical_methods'], row['natural_methods'],row['diseases'])  # Replace column1, column2, ... with your column names
        cursor.execute(query, values)

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    return 'File uploaded successfully', 200

if __name__ == '__main__':
    app.run(debug=True)
