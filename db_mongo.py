from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Conectar a MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client.db_respuestos
collection = db.repuestos

# Buscar repuestos
repuestos = collection.find({"categoria": "RODAMIENTO"})
for repuesto in repuestos:
    print(repuesto)