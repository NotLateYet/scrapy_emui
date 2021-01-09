import pymongo
from config import MongoDBConfig


class MongoDB(object):
    def __init__(self):
        nodes = ','.join(MongoDBConfig.NODES)
        self.__client = pymongo.MongoClient("mongodb://{0}/".format(nodes))

    @property
    def client(self):
        return self.__client


if __name__ == '__main__':
    client = MongoDB().client
    print(client.list_database_names())
    db = client['NotLate']
    print(db.list_collection_names())
    colle = db['notlate2']
    print('update: ', colle.update_one({'name': 'not'}, {'$set': {'name': 'not', 'age': 15}}, upsert=True))
    colle.update_one({'name': 'not1'}, {'$set': {'name': 'not2', 'age': 15}}, upsert=True)
    for doc in colle.find():
        print('find-all', doc)
    for doc in colle.find({'name': 'not2'}):
        print('find-conditon:', doc)
    colle.drop()
    print(db.list_collection_names())
    client.drop_database(db)
    print(client.list_database_names())
