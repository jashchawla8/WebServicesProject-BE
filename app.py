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


@app.route('/dashboard', methods=['POST'])
def dashboard():
    data = request.json
    user_id = data.get('userId')


    # Fetch the user's organization id
    user = db.users.find_one({"userId": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404

    org_id = user['orgId']
    user_projects = user['projectId']

    # Fetch all users in the same organization
    team = list(db.users.find({"orgId": org_id}, {"_id": 0, "userId": 1, "firstName": 1,"lastName":1, "role": 1}))

    # Format team data
    formatted_team = [{"userid": member["userId"], "name": member["firstName"] +" " + member["lastName"], "role": member["role"]} for member in
                      team]

    # Fetch hardware utilization for the organization

    projects = list(db.projects.find({"orgId": org_id, "projectId": {"$in": user_projects}}, {"_id": 0, "projectId": 1, "name": 1, "hwSet1": 1, "hwSet2": 1}))

    print(projects)


    total_org_hw1_utilisation = sum(int(project['hwSet1']) for project in projects)
    total_org_hw2_utilisation = sum(int(project['hwSet2']) for project in projects)

    # Fetch project details

    project_details = [{
        "pid": project['projectId'],
        "name": project['name'],
        "hwset1": int(project['hwSet1']),
        "hwset2": int(project['hwSet2'])
    } for project in projects]

    response = {
        "team": formatted_team,
        "totalOrgHW1Utilisation": total_org_hw1_utilisation,
        "totalOrgHW2Utilisation": total_org_hw2_utilisation,
        "projects": project_details
    }

    return jsonify(response)

@app.route('/dashboard/project', methods=['POST'])
def dashboard():
    data = request.json
    user_id = data.get('userId')

    user = db.users.find_one({"userId": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404

    org_id = user['orgId']
    user_projects = user['projectId']
    projects = list(db.projects.find({"orgId": org_id, "projectId": {"$in": user_projects}}, {"_id": 0, "projectId": 1, "name": 1, "hwSet1": 1, "hwSet2": 1, "date_created": 1}))

    project_details = [{
        "date_created" : project['date_crated'],
        "pid": project['projectId'],
        "name": project['name'],
        "hwset1": int(project['hwSet1']),
        "hwset2": int(project['hwSet2'])
    } for project in projects]

    response = {"projects" : project_details}

    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)

