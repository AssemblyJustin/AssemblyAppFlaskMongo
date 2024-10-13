from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from app import mongo
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pint import UnitRegistry, Quantity

class Trade(BaseModel):
    id: Optional[str] = Field(default=None)
    name: str = Field(..., min_length=1)
    rate: float = Field(..., gt=0)
    uom: str = Field(..., min_length=1)

    @field_validator('uom')
    def validate_uom(cls, v):
        valid_uoms = ['$', '$/hr', '$/day']  # Add more valid units of measure as needed
        if v not in valid_uoms:
            raise ValueError(f'Invalid unit of measure. Must be one of: {", ".join(valid_uoms)}')
        return v

class TradeModel:
    @staticmethod
    def get_all():
        return list(mongo.db.trades.find())

    @staticmethod
    def get_by_id(trade_id):
        return mongo.db.trades.find_one({"_id": ObjectId(trade_id)})

    @staticmethod
    def create(data):
        trade = Trade(**data)
        return mongo.db.trades.insert_one(trade.dict(exclude={'id'}))

    @staticmethod
    def update(trade_id, data):
        trade = Trade(**data)
        return mongo.db.trades.update_one(
            {"_id": ObjectId(trade_id)},
            {"$set": trade.dict(exclude={'id'}, exclude_unset=True)}
        )

    @staticmethod
    def delete(trade_id):
        return mongo.db.trades.delete_one({"_id": ObjectId(trade_id)})

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

class Task(BaseModel):
    id: Optional[str] = Field(default=None)
    trade_id: str
    material_id: str
    description: str
    labour_constant: float

    @field_validator('trade_id', 'material_id')
    def validate_object_id(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return str(v)

class TaskModel:
    @staticmethod
    def get_all():
        return list(mongo.db.tasks.find())

    @staticmethod
    def get_by_id(task_id):
        return mongo.db.tasks.find_one({"_id": ObjectId(task_id)})

    @staticmethod
    def create(data):
        task = Task(**data)
        return mongo.db.tasks.insert_one(task.dict(exclude={'id'}))

    @staticmethod
    def update(task_id, data):
        task = Task(**data)
        return mongo.db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": task.dict(exclude={'id'}, exclude_unset=True)}
        )

    @staticmethod
    def delete(task_id):
        return mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})

class LabourConstant(BaseModel):
    id: Optional[str] = Field(default=None)
    trade: str  # Changed from trade_id to trade
    item: str
    constant: float = Field(..., gt=0)
    uom: str = Field(..., min_length=1)

    @field_validator('trade')
    def validate_trade(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId for trade')
        return str(v)

    @field_validator('uom')
    def validate_uom(cls, v):
        valid_uoms = ['hr/unit', 'hr/m', 'hr/m2', 'hr/m3']  # Add more valid units of measure as needed
        if v not in valid_uoms:
            raise ValueError(f'Invalid unit of measure. Must be one of: {", ".join(valid_uoms)}')
        return v

class LabourConstantModel:
    @staticmethod
    def get_all():
        return list(mongo.db.labour_constants.find())

    @staticmethod
    def get_by_id(labour_constant_id):
        return mongo.db.labour_constants.find_one({"_id": ObjectId(labour_constant_id)})

    @staticmethod
    def create(data):
        labour_constant = LabourConstant(**data)
        return mongo.db.labour_constants.insert_one(labour_constant.dict(exclude={'id'}))

    @staticmethod
    def update(labour_constant_id, data):
        labour_constant = LabourConstant(**data)
        return mongo.db.labour_constants.update_one(
            {"_id": ObjectId(labour_constant_id)},
            {"$set": labour_constant.dict(exclude={'id'}, exclude_unset=True)}
        )

    @staticmethod
    def delete(labour_constant_id):
        return mongo.db.labour_constants.delete_one({"_id": ObjectId(labour_constant_id)})
