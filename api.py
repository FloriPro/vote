from flask import Blueprint
from flask import request
import random
from replit import db
from replit.database.database import ObservedList
from replit.database.database import ObservedDict
import string
import json

app = Blueprint('clientApi', __name__, template_folder='templates')

ws = None


def randomString():
    letters = string.ascii_lowercase
    letters += string.ascii_uppercase
    letters += string.digits
    b = ""
    while b in [
            "", "create", "index", "static", "vote", "favicon.ico",
            "robots.txt"
    ] or b in db:
        b = ''.join(random.choice(letters) for i in range(10))
    return b


def toNormalDict(o):
    d = {}
    for x in o:
        if type(o[x]) == ObservedList:
            d[x] = toNormalList(o[x])
        elif type(o[x]) == ObservedDict:
            d[x] = toNormalDict(o[x])
        else:
            d[x] = o[x]
    return d


def toNormalList(o):
    d = []
    for x in o:
        d.append(x)
    return d


def splitEachInArray(array, delimiter):
    newArray = []
    for i in array:
        s = i.split(delimiter)
        for j in s:
            newArray.append(j)
    return newArray


@app.route("/api")
def api():
    return "api v0.0"


@app.route("/api/endpoint/vote", methods=["POST"])
def vote():
    # get the json of the request
    data = request.get_json()
    voteId = data["voteId"]
    option = data["option"]

    if db[voteId]["type"] == "wordcloud":
        return "404"

    if voteId not in db:
        return "404"

    if option not in db[voteId]["options"]:
        return "404"

    db[voteId]["votes"][option] += 1
    ws.update(voteId, {
        "type": "add",
        "pollType": "chart",
        "option": option,
        "id": voteId
    })
    return "200"


@app.route("/api/endpoint/wordVote", methods=["POST"])
def wvote():
    data = request.get_json()
    voteId = data["voteId"]
    word = data["word"]

    if voteId not in db:
        return "404"

    if db[voteId]["type"] != "wordcloud":
        return "404"

    if word in db[voteId]["taglist"].keys():
        db[voteId]["taglist"][word] = db[voteId]["taglist"][word] + 1
    else:
        db[voteId]["taglist"][word] = 1

    ws.update(
        voteId, {
            "pollType": "wordcloud",
            "id": voteId,
            "taglist": toNormalDict(db[voteId])["taglist"]
        })

    return "200"


@app.route("/api/endpoint/getVote/<voteId>", methods=["GET"])
def getVote(voteId):
    if voteId not in db:
        return "404"
    if db[voteId]["publicResults"] != True:
        return "passw"
    return json.dumps(toNormalDict(db[voteId]))


@app.route("/api/endpoint/getVote/<voteId>/<passw>", methods=["GET"])
def getVotePassw(voteId, passw):
    if voteId not in db:
        return "404"
    if db[voteId]["prpassword"] != passw:
        return "passw wrong"
    return json.dumps(toNormalDict(db[voteId]))


@app.route("/api/create", methods=["POST"])
def create():
    rand = randomString()

    # get the json of the request
    data = request.get_json()
    title = data["title"]
    description = data["description"]
    options = data["options"]
    publicResults = data["publicResults"]
    prpassword = data["prpassword"]
    showType = data["showType"]
    zero = data["zero"]

    options = splitEachInArray(
        splitEachInArray(splitEachInArray(options.split(" ; "), " ;"), "; "),
        ";")

    v = {}
    for x in options:
        v[x] = 0

    db[rand] = {
        "title": title,
        "description": description,
        "options": options,
        "votes": v,
        "publicResults": publicResults,
        "prpassword": prpassword,
        "showType": showType,
        "zero": zero,
        "type": "chart"
    }
    return rand


@app.route("/api/createCloud", methods=["POST"])
def createCloud():
    data = request.get_json()
    title = data["title"]
    description = data["description"]

    rand = randomString()
    db[rand] = {
        "taglist": {},
        "type": "wordcloud",
        "publicResults": True,
        "title": title,
        "description": description,
    }
    return rand
