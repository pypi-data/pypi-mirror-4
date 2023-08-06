# intentionally empty; called on package initialization
from bson.objectid import ObjectId

def new_id():
    return str(ObjectId())