from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from app import mongo
from pydantic import BaseModel, Field
from pint import UnitRegistry, Quantity


class Material:
    @staticmethod
    def get_all():
        return mongo.db.materials.find()

    @staticmethod
    def get_by_id(material_id):
        return mongo.db.materials.find_one({"_id": ObjectId(material_id)})

    @staticmethod
    def create(data):
        return mongo.db.materials.insert_one(data)

    @staticmethod
    def update(material_id, data):
        return mongo.db.materials.update_one({"_id": ObjectId(material_id)}, {"$set": data})

    @staticmethod
    def delete(material_id):
        return mongo.db.materials.delete_one({"_id": ObjectId(material_id)})
