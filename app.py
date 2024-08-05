from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import certifi
import os
import bcrypt
import users
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
    userId = data.get('userId')  # Mapping email to userId
    password = data.get('password')
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    operation = data.get('operation')
    orgId = data.get('orgId')
    orgName = data.get('orgName')

    response, status = users.register_user(db, userId, password, firstName, lastName, operation, orgId, orgName)
    return jsonify(response), status



@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    userId = data.get('userId')
    password = data.get('password')

    response, status = users.login_user(db, userId, password)
    return jsonify(response), status
    return jsonify(response), status

#Project Endpoints

@app.route('/api/project', methods=['POST'])
def get_project():
    data = request.json
    projectId = data.get('projectId')


    response, status = projects.get_project_details(db, projectId)
    return jsonify(response), status


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

@app.route('/dashboard', methods=['POST'])
def dashboard():
    data = request.json
    user_id = data.get('userId')
    response,status = projects.dashboard(db,user_id)
    return jsonify(response), status

@app.route('/dashboard/project', methods=['POST'])
def get_project_list():
    data = request.json
    user_id = data.get('userId')
    response, status = projects.get_project_list(db, user_id)
    return jsonify(response), status


if __name__ == '__main__':
    app.run(debug=True)
