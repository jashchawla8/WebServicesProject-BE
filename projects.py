from flask import jsonify
from pymongo import MongoClient
import users
from datetime import datetime

# Returns all projects from the projects collection
def get_projects(db_object):
    return db_object.projects

def get_project(db_object, project_id):
    project = get_projects(db_object).find_one({"projectId":project_id})
    if not project:
        raise Exception("Project not found")
    return project

def create_project(db_object, project_id, project_name, description, admin_id, userId_list):
    
    projects_handle = get_projects(db_object)
    try: 
        if projects_handle.find_one({"projectId":project_id}):
            raise Exception("Project with this Id, already exists")
    except Exception as e:
        return {"status": 1, "data": "Project with this Id, already exists"}
    
    userId_list.append(admin_id)
    user_jsonlist = []
    try:       
        for user_id in userId_list:
            user = users.get_user(db_object, user_id)
            user_jsonlist.append(user_id)
    except Exception as e:
        return {"status": 1, "data": "One of the members don\'t exist in the system"}

    admin_data = users.get_user(db_object, admin_id)
    project = {
                "projectId": project_id,
                "projectName": project_name,
                "description": description,
                "users": user_jsonlist,
                "hwUtilization": {
                    "set1": 0,
                    "set2": 0
                    },
                "orgId": admin_data["orgId"],
                "dateCreated": datetime.now().isoformat()
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
        "pid": project.get('projectId'),
        "name": project.get('name'),
        "dateCreated": project.get('dateCreated'),
        "hwset1": project.get('hwset1'),
        "hwset2": project.get('hwset2'),
        "description": project.get('description'),
        "members": project.get('members')
    }
    return response, 200

