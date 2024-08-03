from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import certifi
import os
import bcrypt
import projects

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
    project_id = request.json.get('projectId')
    admin_id = request.json.get('userId')
    user_ids = request.json.get('users')


    if not name:
        return jsonify({"error": "Project Name is required"}), 400
    elif not description:
        return jsonify({"error": "Project Description is required"}), 400
    elif not project_id:
        return jsonify({"error": "Project Id is required"}), 400
    elif not admin_id:
        return jsonify({"error": "Project Owner is required"}), 400
    elif not user_ids:
        return jsonify({"error": "Users list is required"}), 400

    result = projects.create_project(db, project_id, name, description, admin_id, user_ids)
    if result["status"] == 0:
        return jsonify({'message': 'Project created with project Id: ' + str(project_id)}), 200
    else: 
        return jsonify({'error': result["data"]}), 500


if __name__ == '__main__':
    app.run(debug=True)
