
from pymongo.mongo_client import MongoClient
import mongoengine
import configparser
from models import Authors, Quotes
import json
import datetime


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    mongo_user = config.get('DB', 'user')
    mongodb_pass = config.get('DB', 'pass')
    db_name = config.get('DB', 'db_name')
    domain = config.get('DB', 'domain')

    uri = f"""mongodb+srv://{mongo_user}:{mongodb_pass}@{domain}/{db_name}?retryWrites=true&w=majority"""
    # Create a new client and connect to the server
    client = MongoClient(uri)
    mongoengine.connect(host = uri)
    db=client["Quotes"]
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    
    return db

def json_into_db(json_file, db):
    with open(json_file, "r") as fh:
        data = json.load(fh)
    if not data:
        return
    if isinstance(data,dict):
        data = [data]
    if "fullname" in data[0].keys():
        for entry in data:
            Authors(fullname=entry['fullname'], born_date=datetime.datetime.strptime(entry['born_date'],"%B %d, %Y"), born_location=entry['born_location'], description=entry['description']).save()
    else:
        collection = db["authors"]
        for entry in data:
            author_id = collection.find_one({"fullname":entry['author']},{"_id":1})
            if not author_id:
                Authors(fullname=entry['author'],born_date=None,born_location=None,description=None).save()
                author_id = collection.find_one({"fullname":entry['author']},{"_id":1})
            Quotes(tags=entry['tags'],author=author_id,quote=entry['quote']).save()

def search_by_tags(db):
    
    command=''
    while True:
        command = input("Give command\n")
        if command == 'exit':
            break
        try: 
            key, value = command.split(':')
        except ValueError:
            continue
        value = value.strip()
        if key in ["fullname","born_location","description"]:
            collection = db["authors"]
            print(collection.find_one({key:value}))
        elif key == "born_date":
            collection = db["authors"]
            date = datetime.datetime.strptime(value,"%B %d, %Y")
            print(collection.find_one({'born_date':date}))
        elif key in ["quote"]:
            collection = db["quotes"]
            print(collection.find_one({key:value}))
        elif key == "tags":
            collection = db["quotes"]
            values = value.split(',')
            for value in values:
                print(collection.find({"tags":value}))

if __name__=='__main__':
    db = main()
    search_by_tags(db)
    
