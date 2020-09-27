import sys
sys.path.append(".")
from flask import Flask, request, Response, render_template
from models.todo import ToDo
from models.task import Task
from models.player import Player
from models.match import Match
from models.playerMatch import PlayerMatch
from werkzeug.exceptions import InternalServerError, BadRequest
from db import db

import json

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:password@db:5432/flaskJWT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

TEAMS_ORDER = ["csk", "dc", "kxip", "kkr", "mi", "rr", "rcb", "srh"]
PASSKEY = "VIT2017"

db.init_app(app)

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


@app.route("/api/v1/todos/<toDoId>", methods=["GET", "PUT", "DELETE"])
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
            return BadRequest("No ToDo matches id {}".format(toDoId))
        return json.dumps(toDo.json())
    except Exception:
        return InternalServerError("Something went wrong!")


def updateToDoItem(toDoId):
    try:
        toDo = ToDo.find_by_id(toDoId)
        if toDo is None:
            return BadRequest("No ToDo matches id {}".format(toDoId))
        body = request.json
        toDo.name = body.get("name")
        toDo.description = body.get("description")
        toDo.save_to_db()
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
            return BadRequest("No ToDo matches id {}".format(toDoId))
        toDo.delete_from_db()
        return Response("ToDo with id {} successfully deleted".format(toDo.id), status=201)
    except Exception:
        return InternalServerError("Something went wrong!")

#-------- fantasy league

@app.route("/api/v1/league/player", methods=["GET","POST"])
def playerResource():
    if request.method == 'POST':
        return createPlayer()
    else:
        return getPlayers()

@app.route("/api/v1/league/player/<id>", methods=["GET"])
def playerMatchHistory(id):
    player = Player.find_by_id(id)
    playerMatches = PlayerMatch.find_by_player(id);
    lis = []
    for playerMatch in playerMatches:
        match = Match.find_by_id(playerMatch.matchId)
        lis.append((playerMatch,match))
    return render_template("playerMatchHistory.html", playerMatches=lis, player=player)

@app.route("/api/v1/league/order", methods=["GET"])
def getOrder():
    players = Player.find_all()
    return json.dumps(TEAMS_ORDER)

@app.route("/api/v1/league/home", methods=["GET"])
def leagueHome():
    players = Player.find_all()
    sortedPlayers = sorted(players, key=lambda x: x.score, reverse=True)
    return render_template("home.html", players=sortedPlayers, order=TEAMS_ORDER)

def createPlayer():
    try:
        body = request.form
        name = body.get("name")
        priorities = body.get("priority")
        password = body.get("pass")
        if password != PASSKEY:
            return Response("Entered password is incorrect", status=201)
        priorities = priorities.split(",")
        existingPlayer = Player.find_by_name(name)
        if existingPlayer:
            return Response("Player already exists, not creating" , status=201)
        pl = Player(name, *priorities)
        pl.save_to_db()
        return Response("Created player with id {}".format(pl.id), status=201)
    except Exception:
        return InternalServerError("Something went wrong")

def getPlayers():
    try:
        players = Player.find_all()
        players = sorted(player, key=lambda x: x.score)
        password = body.get("pass")
        resp = [player.json() for player in players]
        return json.dumps(resp)
    except Exception:
        return InternalServerError("Something went wrong!")

@app.route("/api/v1/league/match", methods=["POST"])
def registerMatch():
    try:
        form = request.form
        winner = form.get("winner")
        loser = form.get("loser")
        password = form.get("pass")
        if password != PASSKEY: 
            return Response("Entered password is incorrect", status=201)
        mt = Match(winner, loser)
        mt.save_to_db()
        players = Player.find_all()
        for player in players:
            points = getattr(player, winner)
            player.score += points
            pm = PlayerMatch(mt.id, player.id, points)
            pm.save_to_db()
            player.save_to_db()
        return Response("Scores updated for all player", status=201)
    except Exception:
        return InternalServerError("Something went wrong, winner key might be non existent")

@app.route("/api/v1/league/player/<id>/score/<score>", methods=["GET"])
def updatePlayerScore(id, score):
    try:
        player = Player.find_by_id(id)
        player.score = score
        player.save_to_db()
        return Response("Score updated for player "+player.name+" new score is:"+str(player.score), status=201)
    except Exception:
        return InternalServerError("Something went wrong, player key might be non existent")

@app.route("/api/v1/league/player/<id>/delete", methods=["GET"])
def deletePlayer(id):
    try:
        player = Player.find_by_id(id)
        player.delete_from_db()
        return Response("Player with name "+player.name+" deleted")
    except Exception as e:
        raise

@app.route("/api/v1/league/match/<id>/delete", methods=["GET"])
def deleteMatch(id):
    try:
        match = Match.find_by_id(id)
        winner = match.winner
        for pl in Player.find_all():
            plmt = PlayerMatch.find_by_player_and_match(pl.id, match.id);
            if plmt:
                plmt.delete_from_db()
            pl.score -= getattr(pl, match.winner)
        match.delete_from_db()
        return Response("Match with id "+str(match.id)+" deleted")
    except Exception as e:
        raise


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    db.init_app(app)
    app.run(host='0.0.0.0', port=5000)
