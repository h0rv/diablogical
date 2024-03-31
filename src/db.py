import plyvel
import json


class JSONDatabase:
    def __init__(self, db_path):
        self.db = plyvel.DB(db_path, create_if_missing=True)

    def __del__(self):
        self.db.close()

    def set(self, key, value):
        self.db.put(key.encode(), json.dumps(value).encode())

    def get(self, key):
        value = self.db.get(key.encode())
        if value:
            return json.loads(value)
        else:
            return None

    def update(self, key, update_func):
        value = self.get(key)
        if value:
            updated_value = update_func(value)
            self.set(key, updated_value)
            return updated_value
        else:
            return None
