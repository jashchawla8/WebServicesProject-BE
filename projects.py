from flask import jsonify
from pymongo import MongoClient
import users
from datetime import datetime
import hardware
from bson.objectid import ObjectId

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

   

    user_handle = users.get_users(db_object)
    try:       
        for user_id in userId_list:
            user = users.get_user(db_object, user_id)

            user_jsonlist.append(user_id)

            temp_list = []
            if user["projectId"] is not None:
                for p_id in user["projectId"]:
                    temp_list.append(p_id)
            temp_list.append(project_id)
            user_handle.update_one({"userId":user["userId"]}, {"$set": {"projectId": temp_list}})

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

    # Convert dateCreated to the desired format if needed
    dateCreated = project.get('dateCreated', '')
    if dateCreated:
        dateCreated = dateCreated
    # Fetch all users in the same organization
    user_array = project.get("users")

    team = list(db.users.find({"userId": {"$in": user_array}}, { "userId": 1, "firstName": 1,"lastName":1, "role": 1}))

    formatted_team = [{"userId": member["userId"], "name": member["firstName"] +" " + member["lastName"], "role": member["role"]} for member in
                      team]
    
    response = {
        "projectId": project.get('projectId'),
        "name": project.get('projectName'),
        "dateCreated": dateCreated,
        "hwset1": project.get('hwUtilization', {}).get("set1", 0),
        "hwset2": project.get('hwUtilization', {}).get("set2", 0),
        "description": project.get('description'),
        "members": formatted_team
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
    formatted_team = [{"userId": member["userId"], "name": member["firstName"] +" " + member["lastName"], "role": member["role"]} for member in
                      team]

    # Fetch hardware utilization for the organization

    projects = list(db.projects.find({"orgId": org_id, "projectId": {"$in": user_projects}}, {"_id": 0, "projectId": 1, "projectName": 1, "hwUtilization.set1": 1, "hwUtilization.set2": 1}))

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
        "projects": project_details,
        "orgId": org_id
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


def upd_resourceAllocation(db_object, project_id, set1_qty, set2_qty):
    projects_handle = get_projects(db_object)
    try:
        project = get_projects(db_object).find_one({"projectId":project_id})
        if not project:
            raise Exception("Project not found")
        
        cur_utilization = project["hwUtilization"]
        if set1_qty > cur_utilization["set1"]:
            result = hardware.update_availability(db_object, "1", set1_qty - cur_utilization["set1"], 0)
            if result["status"] == 1:
                raise Exception(result["data"])
        elif set1_qty < cur_utilization["set1"]:
            result = hardware.update_availability(db_object, "1", cur_utilization["set1"] - set1_qty, 1)
            if result["status"] == 1:
                raise Exception(result["data"])

        if set2_qty > cur_utilization["set2"]:
            result = hardware.update_availability(db_object, "2", set2_qty - cur_utilization["set2"], 0)
            if result["status"] == 1:
                raise Exception(result["data"])
        elif set2_qty < cur_utilization["set2"]:
            result = hardware.update_availability(db_object, "2", cur_utilization["set2"] - set2_qty, 1)
            if result["status"] == 1:
                raise Exception(result["data"])
            
        projects_handle.update_one({"projectId": project["projectId"]}, {"$set":{"hwUtilization": {
            "set1": set1_qty,
            "set2": set2_qty
        }}})
        return {"status": 0, "data": 'Updated project resources.'}


    except Exception as e:
        return {"status": 1, "data": 'Could not update project resources. Error: ' + str(e)}

def delete_project(db, project_id):
    projects_collection = db['projects']
    users_collection = db['users']
    project = get_projects(db).find_one({"projectId": project_id})
    project_utilization = project["hwUtilization"]
    try:
        result_update_1 = hardware.update_availability(db, "1", project_utilization["set1"],
                                                       1)
        result_update_2 = hardware.update_availability(db, "2", project_utilization["set2"],
                                                       1)
        result = projects_collection.delete_one({'projectId': project_id})
        if result.deleted_count == 1 and result_update_1["status"] == 0 and result_update_2['status'] == 0:
            users_collection.update_many(
                {'projectId': project_id},
                {'$pull': {'projectId': project_id}}
            )
            return {'message': 'Project deleted successfully'}, 200
        else:
            return {'error': 'Project not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500
    
def check_project_does_not_exist(db, projectId):
    try:
        project = db.projects.find_one({"projectId": projectId})
        return project is None
    except Exception as e:
        return {'Error occurred: ' + str(e)}

def add_members_to_project(db, projectId, userIds):
    result = db.projects.update_one(
        {"projectId": projectId},
        {"$addToSet": {"users": {"$each": userIds}}}  # Adds all userIds to the users array
    )
    return result



