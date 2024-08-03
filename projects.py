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
    

    
    
