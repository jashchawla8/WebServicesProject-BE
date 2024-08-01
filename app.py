from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import certifi
import os


os.environ['SSL_CERT_FILE'] = certifi.where()

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient('mongodb+srv://harshsharma2413:K0VAuSWYU7Is4E8u@cluster0.qmgfe2f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
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

    user_data = {
        'username': username,
        'password': password
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
    if not user or user['password'] != password:
        return jsonify({"error": "Invalid username or password"}), 400

    return jsonify({"message": "User signed in successfully"}), 200

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
