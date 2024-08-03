from pymongo import MongoClient

# Returns all users from the users collection
def get_users(dbObject):
    return dbObject.users

def get_user(dbObject, userId):

    all_users = get_users(dbObject)
    user = all_users.find_one({"userId": userId})
    if not user:
        raise Exception("user not found!")
    return user