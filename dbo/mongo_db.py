# -*- coding: UTF-8 -*-
import pymongo


class MongoDB(object):
    """
    MongoDB数据库连接池统一入口，支持MongoDB集群
    """

    def __init__(self, nodes):
        self.__nodes = nodes
        nodes_str = ','.join(nodes)
        self.__client = pymongo.MongoClient("mongodb://{0}/".format(nodes_str))

    @property
    def client(self):
        """
        从MongoDB连接池中获取客户端实例
        :return: MongoDB客户端实例
        """
        return self.__client

    @property
    def nodes(self):
        """
        获取MongoDB节点信息
        :return: MongoDB节点信息
        """
        return self.__nodes


if __name__ == '__main__':
    NODES = ['127.0.0.1:27017', ]
    client = MongoDB(NODES).client
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
