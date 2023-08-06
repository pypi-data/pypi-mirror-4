from datetime import datetime, timedelta
from time import sleep
from subprocess import Popen

import pymongo

PORT = 31415

def get_mongo_server():
    return Popen(['mongod', '--quiet', '--port', str(PORT), '--dbpath', 'mongo_data/'])

class Cache:
    def __init__(self, name):
        self.server = get_mongo_server()
        sleep(10) # wait for server to start
        connection = pymongo.MongoClient('localhost', PORT)
        self.collection = connection[name]['cache']

        self.collection.ensure_index(
            [('key', pymongo.DESCENDING)]
        )
        self.collection.ensure_index(
            [('ts', pymongo.DESCENDING)], 
            # expireAfterSeconds=10 # not working
        )
    def __del__(self):
        self.server.terminate()

    def set(self, key, value):
        self.collection.insert({
            'key': key,
            'ts': datetime.now(),
            'value': value
        })

    def get(self, key):
        res = self.collection.find_one({'key': key})
        if datetime.now() - res['ts'] > timedelta(seconds=20):

            return None
        
