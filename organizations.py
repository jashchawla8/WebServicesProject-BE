def check_project_does_not_exist(db, projectId):
    try:
        project = db.projects.find_one({"projectId": projectId})
        return project is None
    except Exception as e:
        return {'Error occurred: ' + str(e)}
    
def check_org_does_not_exist(db, orgId):
    try:
        org = db.organizations.find_one({"orgId": orgId})
        return org is None
    
    except Exception as e:
        return {'Error occurred: ' + str(e)}   