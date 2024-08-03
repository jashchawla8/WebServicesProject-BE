from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import certifi
import os
import bcrypt

from dotenv import load_dotenv
load_dotenv()


os.environ['SSL_CERT_FILE'] = certifi.where()

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient(os.getenv("MONGO_DB_URI"))
db = client['SamosaWebServices']  

@app.route('/')
def home():
    return "Welcome to the Flask MongoDB HyperSphere app"

#User Endpoints

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if db.users.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 400
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_data = {
        'username': username,
        'password': hashed_password 
    }

    db.users.insert_one(user_data)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = db.users.find_one({"username": username})
    if not user:
        return jsonify({"error": "Invalid username or password"}), 400

    # Ensure user['password'] is in bytes
    hashed_password = user['password']
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    # Check if the provided password matches the hashed password
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        return jsonify({"message": "User signed in successfully"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 400
    

#Project Endpints

@app.route('/api/projects', methods=['POST'])
def create_project():
    name = request.json.get('name')
    description = request.json.get('description')
    project_id = request.json.get('projectID')


    if not name or not description or not project_id:
        return jsonify({"error": "All fields are required"}), 400

    project = {
        'name': name,
        'description': description,
        'projectID': project_id,
    }
    db.projects.insert_one(project)
    return jsonify({'message': 'Project created successfully', 'project_id': project_id}), 201


if __name__ == '__main__':
    app.run(debug=True)
