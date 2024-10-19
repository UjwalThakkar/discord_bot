import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Toxicity_detector"]
server_collection = db['servers']
dataset = db['Dataset']
MAX_RECENT_STRIKES = 3


def add_user(user, message):
    print(user)
    


def handle_user(user_id, user_name, message, toxic_classes):
    user_doc = server_collection.find_one({'uid': user_id})
    if(user_doc == None):
        user_doc = server_collection.insert_one({"uid": user_id, "user_name": str(user_name), "messages": [{"message": str(message), "type": toxic_classes}]})
    else:
       print(toxic_classes)
       user_doc = server_collection.find_one_and_update({'uid': user_id}, {'$push': {'messages': {"message":  str(message), "type": toxic_classes}}})
        
    return user_doc

def handle_report(message_id, message, toxic_classes):
    try:
        # Create the document to insert
        document = {
            "text_id": message_id,
            "text": message,
            "flags": toxic_classes
        }

        # Insert the document into the Dataset collection
        dataset.insert_one(document)

        # Optionally, you can print a confirmation or log it
        print(f"Report inserted successfully for message ID: {message_id}")
    except Exception as e:
        print(f"An error occurred while inserting the report: {e}")