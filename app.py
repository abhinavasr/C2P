import os
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*.mastercard.com"}})

i_tems = [
        { 'name': 'Mango', 'price': round(random.uniform(1, 5), 2) },
        { 'name': 'Banana', 'price': round(random.uniform(1, 5), 2) },
        { "name": "Apple", "price": round(random.uniform(1, 5), 2) },
        { "name": "Orange", "price": round(random.uniform(1, 5), 2) },
        { "name": "Grapes", "price": round(random.uniform(1, 5), 2) },
        { "name": "Pineapple", "price": round(random.uniform(1, 5), 2) },   
    ]

@app.route('/')
def index():
# Generate a random value between 1 and 5 for each item
    e_mail = "abhinava.srivastava@mastercard.com"
    return render_template('index.html', items=i_tems, email=e_mail)


@app.route('/getlist')
def getList():
    return jsonify(i_tems)


@app.route('/checkout', methods=['POST'])
def checkout():
    # Get the input parameter from the POST request data as JSON
    # Print the input parameter to the console
    input_param = request.get_json()
    print(input_param)
    link_id = db.store_data(input_param)
    print(link_id)
    access_url = "https://app.abhinava.xyz/access_data/"+link_id
    print(access_url)
    return jsonify({"Payment URL": access_url})

# Make a route for the checkoutAPI (/checkoutAPI), capture the input parameter as post param and print it

@app.route('/checkoutAPI', methods=['POST'])
def checkoutAPI():
    # Get the input parameter from the POST request data as JSON
    # Process payments here
    return {"result":"Okay"}
       

@app.route('/access_data/<string:link_id>', methods=['GET'])
def access_data_route(link_id):
    i_tems = db.retrieve_data(link_id)
    return render_template('index.html', items=i_tems, email="abhinava.srivastava@mastercard.com")


@app.route('/<path:filename>')
def serve_static(filename):
    print(filename)
    return send_from_directory('static', filename)

from db_access import Storage
db = Storage()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
