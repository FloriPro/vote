from replit import db
import json
d = input("db: ")

db[d]=json.loads(db[d])