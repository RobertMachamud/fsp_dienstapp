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


@app.route("/register_dancer", methods=["GET", "POST"])
def register_dancer():
    if request.method == "POST":
        # checking if username already exist in db
        user_exists = mongo.db.ballett.find_one(
            {"$and": [
                {"f_name": request.form.get("f_name").lower()},
                {"l_name": request.form.get("l_name").lower()},
                {"email": request.form.get("email")}
            ]}
        )
        # redirecting back if user already exists
        if user_exists:
            flash("Sorry, this Dancer is already registered")
            return redirect(url_for("register_dancer"))

        # Obj for dancer
        register_dancer = {
            "personal_data": {
                "name": {
                    "f-name": request.form.get("f-name").lower(),
                    "l-name": request.form.get("l-name").lower(),
                },
                "contact_data": {
                    "address": {
                        "street": request.form.get("street").lower(),
                        "h-number": request.form.get("h-number"),
                        "plz": request.form.get("plz"),
                        "city": request.form.get("city").lower(),
                    },
                    "email": request.form.get("email").lower(),
                    "dob": request.form.get("dob").lower(),
                    "tel": request.form.get("tel"),
                }
            },
            "nationality": request.form.get("nationality").lower(),
            "pob": request.form.get("pob").lower(),
            "sex": request.form.get("sex").lower(),
            "gender": request.form.get("gender").lower(),
            "parent": request.form.get("parent"),
            "e": 0,
            "dances": {
                "all_dances": [],
                "amt_dances": 0,
                "a_cast": [],
                "b_cast": [],
                "b_cast_counter": [],
            },
            "ballett_training": {
                "e_dates": [],
                "present": True,
                "e_used_today": False,
            },
            "urlaubstage": 0,
            "status": "present",
            "personal_messenges": [],
            "notes": []
        }
        # creating and adding to obj above - full name and short form
        first_name = register_dancer["personal_data"]["name"]["f_name"]
        last_name = register_dancer["personal_data"]["name"]["l_name"]
        # full name
        register_dancer["personal_data"]["name"]["full_name"] = first_name + last_name
        # short form
        register_dancer["personal_data"]["name"]["short_form"] = first_name + last_name[0]

        # creating and adding to obj above - username (combination of full name & rand num)
        username = first_name + last_name + randint(0,9)
        # username
        register_dancer["personal_data"]["name"]["username"] = username

        # creating and adding to obj above - password (full name, no space)
        register_dancer["password"] = generate_password_hash(
            first_name + last_name)

        # inserting/adding new dancer to DB
        mongo.db.ballett.insert_one(register_dancer)

        # putting new user into session cookie
        session["user"] = username
        return redirect(url_for("/", username=session["user"]))

    return render_template("register_dancer.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # checking if username in db
        user_exists = mongo.db.users.find_one(
            {"email": request.form.get("email")})

        if user_exists:
            # checking if password is matching user input
            if check_password_hash(
                    user_exists["password"], request.form.get("password")):
                session["user"] = user_exists["password"]
                # flash()
                return redirect(url_for("/", username=session["user"]))
            else:
                flash("Username and/or Password incorrect")
                return redirect(url_for("login"))

        else:
            # in case username doesn't exists
            flash("Username and/or Password incorrect")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # removing user from sessions cookies
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/ballett")
def ballett():
    # lists of whole ballett
    ballett = list(mongo.db.ballett.find())
    kranke = list(mongo.db.ballett.find({'status':'krank'}))
    return render_template("ballett.html", ballett=ballett, kranke=kranke)


@app.route("/abw_dancernames", methods=["GET", "POST"])
def abw_dancernames():
    abw_names = mongo.db.ballett.find({"ballett_training.present": False})

    if request.method == "POST":
        print("hellooooooooooo")
        mongo.db.ballett.updateMany({"ballett_training.present": False}, {"$set": { "ballett_training.present": True }})
        return redirect(url_for("training_anw"))
        # all_abw_dancers = mongo.db.find({"ballett_training.present": False})
        # for abw_dancer in all_abw_dancers:

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