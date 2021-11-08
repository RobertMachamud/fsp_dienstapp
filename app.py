import os
import random
from datetime import date
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
def index():
    # landing page
    return render_template("index.html")


@app.route("/ballett")
def ballett():
    # lists of whole ballett
    ballett = list(mongo.db.ballett.find())
    kranke = list(mongo.db.ballett.find({'status':'krank'}))
    return render_template("ballett.html", ballett=ballett, kranke=kranke)


@app.route("/abw_dancernames")
def abw_dancernames():
    abw_names = mongo.db.ballett.find({"ballett_training.present": False})
    return render_template("abw_dancernames.html", abw_names=abw_names)


@app.route("/training_anw", methods=["GET", "POST"])
def training_anw():
    # date vars
    raw_date = date.today()
    curr_date = raw_date.strftime("%d/%m/%Y")
    # data list vars
    not_present = []
    ballett = list(mongo.db.ballett.find())
    kranke = list(mongo.db.ballett.find({'status':'krank'}))

    if request.method == "POST":
        abw_id_list = request.form.get("to-backend-not-anw").strip().split(",")
        abw_id_list = list(filter(None, abw_id_list))
        #
        if len(abw_id_list) > 0:
            print("FFFOOOOOOORRRRRRR")
            for abw_id in abw_id_list:
                mongo.db.ballett.update({"_id": ObjectId(abw_id)}, {"$set": {"ballett_training.present": False}})
            not_present = mongo.db.ballett.find({"ballett_training.present": False})
            print(not_present)
        return redirect(url_for("abw_dancernames"))

    # loops t
    for dancer in ballett:
            curr_dancer_id = dancer["_id"]
            for e_date in dancer["ballett_training"]["e_dates"]:
                if e_date == curr_date:
                    mongo.db.ballett.update({"_id": ObjectId(curr_dancer_id)},{"$set": { "ballett_training.e_used_today": True }})
    # all e dancers list
    e_today = list(mongo.db.ballett.find({"ballett_training.e_used_today": {"$eq": True}}))
    return render_template("training_anw.html", ballett=ballett, kranke=kranke, e_today=e_today, not_present=not_present)
    

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)


# print(dancer["ballett_training"]["e_used_today"], dancer["ballett_training"])
                    # mongo.db.ballett.update({"_id": ObjectId(curr_dancer_id)},{"$push": { "ballett_training.e_dates": 5 }})