import base64
import plyvel

# Open the LevelDB database
db = plyvel.DB("data/db", create_if_missing=False)

# Iterate over all keys in the database
for key in db.iterator(include_value=False):
    decoded_key = base64.b64decode(key).decode("utf-8")
    print(decoded_key)

# Close the LevelDB database
db.close()
