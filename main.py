from flask import Flask, render_template, redirect
import envs
from replit import db
from api import app as userApi
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(userApi)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<string:voteId>")
def vote(voteId):
    if voteId not in db:
        return render_template("404.html")

    title = db[voteId]["title"]
    description = db[voteId]["description"]
    options = db[voteId]["options"]

    return render_template("vote.html", voteId=voteId, title=title, description=description, options=options)


@app.route("/<string:voteId>/results")
def results(voteId):
    if voteId not in db:
        return render_template("404.html")

    if db[voteId]["publicResults"] == False:
        return render_template("privateResult.html")

    title = db[voteId]["title"]
    description = db[voteId]["description"]
    options = db[voteId]["options"]
    votes = db[voteId]["votes"]
    
    return render_template("results.html", voteId=voteId, title=title, description=description, options=options, votes=votes)


@app.route("/<string:voteId>/results/<string:password>")
def resultsPassword(voteId, password):
    if voteId not in db:
        return render_template("404.html")

    if db[voteId]["publicResults"] == True:
        return render_template("publicResult.html")

    if db[voteId]["prpassword"] != password:
        return redirect(f"/{voteId}/results")

    title = db[voteId]["title"]
    description = db[voteId]["description"]
    options = db[voteId]["options"]
    votes = db[voteId]["votes"]

    # cap the votes at 3 to force the user to go to flulu.eu
    cap = False
    v = {}
    for i in votes:
        if votes[i] > 3:
            v[i] = ">3"
            cap = True
        else:
            v[i] = votes[i]

    return render_template("results.html", voteId=voteId, title=title, description=description, options=options, votes=v, cap=cap)


@app.route("/create")
def create():
    return render_template("create.html")


# put flask in debug mode
app.debug = True


app.run("0.0.0.0", 81)
