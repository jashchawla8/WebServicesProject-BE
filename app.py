from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import certifi
import os
import bcrypt


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
    userId = data.get('userId')  # Mapping email to userId
    password = data.get('password')
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    operation = data.get('operation')
    orgId = data.get('orgId')
    orgName = data.get('orgName')
    role = "Admin" if operation == "create" else "Member"
    projectId = []  # Initially empty

    if not userId or not password or not firstName or not lastName or not operation or not orgId:
        return jsonify({"error": "All fields are required"}), 400

    if db.users.find_one({"userId": userId}):
        return jsonify({"error": "User ID already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if operation == "create":
        if not orgName:
            return jsonify({"error": "Organization name is required for creation"}), 400

        if db.organizations.find_one({"orgId": orgId}):
            return jsonify({"error": "Organization already exists"}), 400

        org_data = {
            'orgId': orgId,
            'orgName': orgName
        }
        db.organizations.insert_one(org_data)

    elif operation == "join":
        org = db.organizations.find_one({"orgId": orgId})
        if not org:
            return jsonify({"error": "No organization found with the given orgId"}), 400

    else:
        return jsonify({"error": "Invalid operation"}), 400

    user_data = {
        'userId': userId,
        'password': hashed_password,
        'role': role,
        'orgId': orgId,
        'projectId': projectId,
        'firstName': firstName,
        'lastName': lastName
    }
    db.users.insert_one(user_data)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    userId = data.get('userId')
    password = data.get('password')

    if not userId or not password:
        return jsonify({"error": "User ID and password are required"}), 400

    user = db.users.find_one({"userId": userId})
    if not user:
        return jsonify({"error": "Invalid User ID or password"}), 400

    # Ensure user['password'] is in bytes
    hashed_password = user['password']
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    # Check if the provided password matches the hashed password
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        return jsonify({"message": "User signed in successfully"}), 200
    else:
        return jsonify({"error": "Invalid User ID or password"}), 400
    
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

# Project Login
@app.route('/api/project-login', methods=['POST'])
def project_login():
    data = request.json
    project_id = data.get('projectID')

    if not project_id:
        return jsonify({"error": "ProjectID is required"}), 400

    project = db.projects.find_one({"projectID": project_id})
    if not project:
        return jsonify({"error": "Invalid projectID"}), 400

    return jsonify({"message": "Logged in to project successfully", "project": project}), 200


if __name__ == '__main__':
    app.run(debug=True)
