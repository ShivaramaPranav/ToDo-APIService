import sys
sys.path.append(".")
from flask import Flask, request, Response
from models.todo import ToDo
from models.task import Task
from werkzeug.exceptions import InternalServerError
from db import db

import json

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:password@db:5432/flaskJWT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'


@app.route("/")
def home():
    return "ToDo API Server up and running!"


@app.route("/api/v1/todos", methods=["POST", "GET"])
def todoResource():
    if request.method == 'POST':
        return createToDo()
    else:
        return getToDos()


def getToDos():
    try:
        toDos = ToDo.find_all()
        resp = [toDo.json() for toDo in toDos]
        return json.dumps(resp)
    except Exception:
        return InternalServerError("Something went wrong!")


def createToDo():
    try:
        body = request.json
        name = body.get("name")
        description = body.get("description")
        tasks = body.get("tasks")
        toDo = ToDo(name=name, description=description)
        toDo.save_to_db()
        taskList = []
        for task in tasks:
            tsk = Task(name=task.get("name"), toDoId=toDo.id, description=task.get("description"))
            tsk.save_to_db()
            taskList.append(tsk)
        return Response("Created ToDo with id {}".format(toDo.id), status=201)
    except Exception:
        return InternalServerError("Something went wrong")


@app.route("/api/v1/todo/<toDoId>", methods=["GET", "PUT", "DELETE"])
def todoItemResource(toDoId):
    if request.method == "GET":
        return getToDoItem(toDoId)
    elif request.method == "PUT":
        return updateToDoItem(toDoId)
    elif request.method == "DELETE":
        return deleteToDoItem(toDoId)


def getToDoItem(toDoId):
    try:
        toDo = ToDo.find_by_id(int(toDoId))
        if toDo is None:
            return Response("No ToDo matches id {}".format(toDo.id), status=201)
        return json.dumps(toDo.json())
    except Exception:
        return InternalServerError("Something went wrong!")


def updateToDoItem(toDoId):
    try:
        toDo = ToDo.find_by_id(toDoId)
        if toDo is None:
            return Response("No ToDo matches id {}".format(toDo.id), status=201)
        body = request.json
        toDo.name = body.get("name")
        toDo.description = body.get("description")
        toDo.save_to_db()
        if toDo is not None:
            toDo.delete_tasks()
        tasks = body.get("tasks")
        for task in tasks:
            tsk = Task(name=task.get("name"), toDoId=toDo.id, description=task.get("description"))
            tsk.save_to_db()
        return Response("ToDo with id {} successfully updated".format(toDo.id), status=201)
    except Exception:
        return InternalServerError("Something went wrong")


def deleteToDoItem(toDoId):
    try:
        toDo = ToDo.find_by_id(int(toDoId))
        if toDo is None:
            return Response("No ToDo matches id {}".format(toDo.id), status=201)
        toDo.delete_from_db()
        return Response("ToDo with id {} successfully deleted".format(toDo.id), status=201)
    except Exception:
        return InternalServerError("Something went wrong!")


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    db.init_app(app)
    app.run(host='0.0.0.0', port=5000)