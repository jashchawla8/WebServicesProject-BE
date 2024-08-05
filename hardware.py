import os
from flask import jsonify
from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

# Returns a handle to the hardware collection in the DB
def get_Hardware(db_object):
    return db_object.hardware

# Operation: 0 -> request hardware, 1 -> return hardware quantity
# 
def update_availability(db_object, hw_set, qty, operation):
    hw_handle = get_Hardware(db_object)
    print('hwset: ' + str(hw_set) + 'qty: ' + str(qty))
    try:
        hw_instance = hw_handle.find_one({"instanceId":hw_set})
        if not hw_instance:
            raise Exception("Hardware instance not found")
        if operation == 0:
            resQty = hw_instance["utilization"] + qty
        elif operation == 1:
            resQty = hw_instance["utilization"] - qty
        else:
            raise Exception("Invalid operation, can only request or return hardware")

        if resQty <0 or resQty >hw_instance["capacity"]:
            raise Exception("Invalid quantity for operation: " + str(operation))

        hw_handle.update_one({"instanceId":hw_set}, {"$set": {"utilization": resQty}})    
        return {"status": 0, "data":'Hardware availability was updated. Total: '+str(hw_instance["capacity"]) + 'Available: ' + str(resQty)}
    
    
    except Exception as e:
        return {"status": 1, "data": 'Could not update availability. Error: ' + str(e)}
    
def get_hwAvailability(db_object):
    hw_handle = get_Hardware(db_object)
    try:
        instance1 = hw_handle.find_one({"instanceId":str(os.getenv("HWSET1_INSTANCE_ID"))})
        instance2 = hw_handle.find_one({"instanceId":str(os.getenv("HWSET2_INSTANCE_ID"))})
        if not instance1 or not instance2:
           raise Exception("Could not find hardware instance(s)") 
    except Exception as e:
        return {"status": 1, "data":str(e)}
    
    return {"status": 0, "data":{
        "hwset1": instance1["capacity"] - instance1["utilization"],
            "hwset2":instance2["capacity"] - instance2["utilization"]
            }
            }