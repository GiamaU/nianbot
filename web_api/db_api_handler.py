from pymongo import MongoClient
import os

cluster = "mongodb+srv://{}:{}@nianbotdb-ivdrl.gcp.mongodb.net/test?retryWrites=true&w=majority"


class dbApiH:

    def __init__(self):
        self.cluster = MongoClient(cluster.format(os.getenv('db_username'), os.getenv('db_password')))
        self.db = None

    ##--GENERAL--##

    def set_db(self, db_name):
        self.db = self.cluster[db_name]

    def get_document_by_name(self, collection_name):
        if collection_name is None:
            return None
        return self.db[collection_name].find({})

    def get_document_by_id(self, collection_name, id):
        if collection_name is None or id is None:
            return None
        return self.db[collection_name].find_one({"_id": id})

    def delete_all_documents(self, collection_name):
        if collection_name is None:
            return
        self.db[collection_name].delete_many({})

    def delete_document_by_id(self, collection_name, id):
        if collection_name is None:
            return
        self.db[collection_name].delete_one({"_id": id})

    ##--USERS--##

    def add_users(self, users):
        self.db["users"].insert_many([{
            "_id": user.id,
            "name": user.name,
            "joined_at": user.joined_at,
            "messages_sent": 0,
            "commands_used": 0,
            "strikes": 0
        } for user in users], ordered=False)

    def add_user(self, user):
        self.db["users"].insert_one({
            "_id": user.id,
            "name": user.name,
            "joined_at": user.joined_at,
            "messages_sent": 0,
            "commands_used": 0,
            "strikes": 0
        })

    def get_alarmed_users(self):
        return self.db["users"].find({"strikes": {"$gt": 0}})

    def get_alarmed_user_by_id(self, id):
        return self.db["users"].find_one({"_id": id, "strikes": {"$gt": 0}})

    def update_user_name_by_id(self, id, new_name):
        self.db["users"].update_one({"_id": id}, {"$set": {"name": new_name}})

    def alarm_user_by_id(self, id):
        self.db["users"].update_one({"_id": id}, {"$inc": {"strikes": 1}})

    def unalarm_user_by_id(self, id):
        self.db["users"].update_one({"_id": id}, {"$inc": {"strikes": -1}})

    def increase_user_messages_by_id(self, id):
        self.db["users"].update_one({"_id": id}, {"$inc": {"messages_sent": 1}})

    def decrease_user_messages_by_id(self, id):
        self.db["users"].update_one({"_id": id}, {"$inc": {"messages_sent": -1}})

    def increase_used_commands_by_id(self, id):
        self.db["users"].update_one({"_id": id}, {"$inc": {"commands_used": 1}})

    def get_top_10_users(self):
        return self.db["users"].find({}).sort([("messages_sent", -1), ("commands_used", -1)]).limit(10)

    def get_all_sent_messages(self):
        return list(self.db["users"].aggregate([{"$group": {"_id": "null", "totalAmount": {"$sum": '$messages_sent'}}}]))

    def get_all_used_commands(self):
        return list(self.db["users"].aggregate([{"$group": {"_id": "null", "totalAmount": {"$sum": 'commands_used'}}}]))

    ##--VIDEOS--##

    def add_videos(self, videos):
        self.db["videos"].insert_many([{
            "_id": video['id'],
            "title": video['title']
        } for video in videos], ordered=False)

    def add_video(self, video):
        self.db["videos"].insert_one({
            "_id": video['id'],
            "title": video['title']
        })

    ##--Q/A--##
