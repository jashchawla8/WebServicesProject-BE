from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import certifi
import os
import bcrypt
import users
import projects
import hardware
import organizations



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

#Project Endpoints

@app.route('/api/project', methods=['POST'])
def get_project():
    data = request.json
    projectId = data.get('projectId')


    response, status = projects.get_project_details(db, projectId)
    return jsonify(response), status


@app.route('/api/project/create', methods=['POST'])
def create_project():
    name = request.json.get('name')
    description = request.json.get('description')
    project_id = request.json.get('projectId')
    admin_id = request.json.get('userId')
    user_ids = request.json.get('users')
     
    print("user Ids" + str(user_ids))

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

    result = projects.create_project(db, str(project_id), name, description, admin_id, user_ids)
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

@app.route('/api/project/resources', methods=['POST'])
def modify_resources():
    project_id = request.json.get('projectId')
    qty_set1 = request.json.get('hwset1')
    qty_set2 = request.json.get('hwset2')
    if not project_id or not qty_set1 or not qty_set2:
        return jsonify({'error': 'Missing required parameters'}), 500
    result = projects.upd_resourceAllocation(db, project_id, qty_set1, qty_set2)
    if result["status"] == 0:
        return jsonify({'message': 'Resource allocation updated for project'}), 200
    else: 
        return jsonify({'error': result["data"]}), 500
    

@app.route('/api/hardware', methods=['GET'])
def get_hwAvailability():
    result = hardware.get_hwAvailability(db)
    if result["status"] == 1:
        return jsonify({'error': result["data"]}), 500
    
    return jsonify(result["data"]), 200

@app.route("/api/project/delete", methods=['POST'])
def delete_project():
    data = request.get_json()
    projectId = data.get('projectId')
    response, status = projects.delete_project(db, projectId)
    return jsonify(response), status

@app.route('/api/check-projectid', methods=['POST'])
def check_projectid():
    data = request.json
    projectId = data.get('projectId')

    if not projectId:
        return jsonify({"error": "Project ID is required"}), 400

    project_exists = projects.check_project_does_not_exist(db, projectId)
    if project_exists:
        return jsonify({"message": "Project does not exist"}), 500
    else:
        return jsonify({"message": "Project exists"}), 200
    
@app.route('/api/check-orgid', methods=['POST'])
def check_orgid():
    data = request.json
    orgId = data.get('orgId')

    if not orgId:
        return jsonify({"error": "Organization ID is required"}), 400

    org_exists = organizations.check_org_does_not_exist(db, orgId)
    if org_exists:
        return jsonify({"message": "Organization does not exist"}), 500
    else:
        return jsonify({"message": "Organization exists"}), 200
    
@app.route('/api/add-members', methods=['POST'])
def add_members_to_project_route():
    data = request.json
    userIds = data.get('members')
    projectId = data.get('projectId')

    if not userIds or not isinstance(userIds, list):
        return jsonify({"error": "User IDs are required and must be a list"}), 400
    if not projectId or not isinstance(projectId, str):
        return jsonify({"error": "Project ID is required and must be a string"}), 400

    # Pass the db connection to the project function
    result = projects.add_members_to_project(db, projectId, userIds)
    if result.matched_count == 0:
        return jsonify({"error": f"Project with ID {projectId} not found"}), 404

    # Pass the db connection to the user function
    success, failed_userId = users.add_project_to_users(db, projectId, userIds)
    if not success:
        return jsonify({"error": f"User with ID {failed_userId} not found"}), 404

    return jsonify({"message": "Users added to project successfully"}), 200

        
if __name__ == '__main__':
    app.run(debug=True)
