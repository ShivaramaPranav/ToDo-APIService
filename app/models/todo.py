import sys
sys.path.append("..")

from db import db
from models.task import Task

class ToDo(db.Model):
    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(100))

    def __init__(self, name, description=''):
        self.name = name
        self.description = description

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        self.delete_tasks()
        db.session.delete(self)
        db.session.commit()
    
    def delete_tasks(self):
        tasks = Task.query.filter_by(toDoId=self.id).all()
        for task in tasks:
            task.delete_from_db()
    
    def json(self):
        taskJson = []
        tasks = Task.query.filter_by(toDoId=self.id).all()
        for task in tasks:
            taskJson.append(task.json())
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": taskJson
        }