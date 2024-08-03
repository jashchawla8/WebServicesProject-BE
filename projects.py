from flask import jsonify
from pymongo import MongoClient
import users

# Returns all projects from the projects collection
def get_projects(db_object):
    return db_object.projects

def create_project(db_object, project_id, project_name, description, admin_id, userId_list:list):

    projects_handle = get_projects(db_object)
    if projects_handle.find_one({"project_id":project_id}):
        raise Exception("Project with this Id, already exists")
    
    userId_list.append(admin_id)
    try:       
        for user_id in userId_list:
            user = users.get_user(db_object, user_id)
    except Exception as e:
        return jsonify({'message': 'One of the members don\'t exist in the system'}), 500

    admin_data = users.get_user(db_object, admin_id)

    project = {
                "project_id": project_id,
                "project_name": project_name,
                "description": description,
                "users": users.append(admin_id),
                "hwUtlization": {
                    "set1": 0,
                    "set1": 0
                    },
                "orgId": admin_data.orgId 
            }
    
    projects_handle.insert_one(project)
    return jsonify({'message': 'Project was created with id: ' + project_id}), 200
    

    
    
