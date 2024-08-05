from flask import jsonify
from pymongo import MongoClient
import users

# Returns all projects from the projects collection
def get_projects(db_object):
    return db_object.projects

def get_project(db_object, project_id):
    project = get_projects(db_object).find_one({"projectId":project_id})
    if not project:
        raise Exception("Project not found")
    return project

def create_project(db_object, project_id, project_name, description, admin_id, userId_list:list):
    
    projects_handle = get_projects(db_object)
    try: 
        if projects_handle.find_one({"project_id":project_id}):
            raise Exception("Project with this Id, already exists")
    except Exception as e:
        return {"status": 1, "data": "Project with this Id, already exists"}
    
    userId_list.append(admin_id)
    try:       
        for user_id in userId_list:
            user = users.get_user(db_object, user_id)
    except Exception as e:
        return {"status": 1, "data": "One of the members don\'t exist in the system"}

    admin_data = users.get_user(db_object, admin_id)
    print(admin_data)

    project = {
                "project_id": project_id,
                "project_name": project_name,
                "description": description,
                "users": userId_list.append(admin_id),
                "hwUtlization": {
                    "set1": 0,
                    "set1": 0
                    },
                "orgId": admin_data["orgId"] 
            }
    
    projects_handle.insert_one(project)
    return {"status": 0, "data": 'Project was created with id: ' + str(project_id)}
    



def get_project_details(db, projectId):
    if not projectId:
        return {"error": "Project ID is required"}, 400

    project = db.projects.find_one({"projectId": projectId})
    if not project:
        return {"error": "Project not found"}, 404

    response = {
        "projectId": project.get('projectId'),
        "name": project.get('projectName'),
        "dateCreated": project.get('dateCreated'),
        "hwset1": project.get('hwUtilization')["set1"],
        "hwset2": project.get('hwUtilization')["set2"],
        "description": project.get('description'),
        "members": project.get('users')
    }
    return response, 200


def dashboard(db, user_id):

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

    projects = list(db.projects.find({"orgId": org_id, "projectId": {"$in": user_projects}}, {"_id": 0, "projectId": 1, "projectName": 1, "hwUtilization.set1": 1, "hwUtilization.set2": 1}))



    print(projects)

    total_org_hw1_utilisation = sum(int(project['hwUtilization']['set1']) for project in projects)
    total_org_hw2_utilisation = sum(int(project['hwUtilization']['set2']) for project in projects)

    # Fetch project details

    project_details = [{
        "projectId": project['projectId'],
        "name": project['projectName'],
        "hwset1": int(project['hwUtilization']['set1']),
        "hwset2": int(project['hwUtilization']['set2'])
    } for project in projects]

    response = {
        "team": formatted_team,
        "totalOrgHW1Utilisation": total_org_hw1_utilisation,
        "totalOrgHW2Utilisation": total_org_hw2_utilisation,
        "projects": project_details
    }

    return response,200



def get_project_list(db, user_id):
    user = db.users.find_one({"userId": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404

    org_id = user['orgId']
    user_projects = user['projectId']
    projects = list(db.projects.find({"orgId": org_id, "projectId": {"$in": user_projects}}, {"_id": 0, "projectId": 1, "projectName": 1,"hwUtilization.set1": 1, "hwUtilization.set2": 1, "dateCreated": 1}))

    project_details = [{
        "dateCreated" : project['dateCreated'],
        "projectId": project['projectId'],
        "name": project['projectName'],
        "hwset1": int(project['hwUtilization']['set1']),
        "hwset2": int(project['hwUtilization']['set2'])
    } for project in projects]

    response = {"projects" : project_details}

    return response, 200



