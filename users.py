import bcrypt
from pymongo import MongoClient

def register_user(db, userId, password, firstName, lastName, operation, orgId, orgName=None):
    role = "Admin" if operation == "create" else "Member"
    projectId = []  # Initially empty

    if not userId or not password or not firstName or not lastName or not operation or not orgId:
        return {"error": "All fields are required"}, 400

    if db.users.find_one({"userId": userId}):
        return {"error": "User ID already exists"}, 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if operation == "create":
        if not orgName:
            return {"error": "Organization name is required for creation"}, 400

        if db.organizations.find_one({"orgId": orgId}):
            return {"error": "Organization already exists"}, 400

        org_data = {
            'orgId': orgId,
            'orgName': orgName
        }
        db.organizations.insert_one(org_data)

    elif operation == "join":
        org = db.organizations.find_one({"orgId": orgId})
        if not org:
            return {"error": "No organization found with the given orgId"}, 400

    else:
        return {"error": "Invalid operation"}, 400

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
    return {"message": "User registered successfully"}, 201

def login_user(db, userId, password):
    if not userId or not password:
        return {"error": "User ID and password are required"}, 400

    user = db.users.find_one({"userId": userId})
    if not user:
        return {"error": "Invalid User ID or password"}, 400

    # Ensure user['password'] is in bytes
    hashed_password = user['password']
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    # Check if the provided password matches the hashed password
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        return {"message": "User signed in successfully"}, 200
    else:
        return {"error": "Invalid User ID or password"}, 400
    


# Returns all users from the users collection
def get_users(dbObject):
    return dbObject.users

def get_user(dbObject, userId):

    all_users = get_users(dbObject)
    user = all_users.find_one({"userId": userId})
    if not user:
        raise Exception("user not found!")
    return user