import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, request, make_response
from flask_session import Session
from datetime import datetime
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import random

from helpers import apology, login_required


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#app.jinja_env.globals.update(function=function)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

@app.route("/char", methods=["GET", "POST"])
@login_required
def char():

    session['number'] = 0

    if request.method == "POST":

        if request.form.get("next"):
            session['number'] = 1
            session.modified = True

        if request.form.get('prev'):
            session['number'] = 0
            session.modified = True

    return redirect('/')

@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    #checking if characters exist, if not, then redirect user to the character creation page
    if not db.execute("SELECT name FROM characters WHERE user_id = :user_id", user_id = session["user_id"]):
        session['character_created'] = 'no'
        return redirect("/create")
    else:
        session['character_created'] = 'yes'

    #list of characters player has (2 characters is the max)
    session['list_char'] = db.execute("SELECT name FROM characters WHERE user_id = :user_id", user_id = session["user_id"])

    #remembering player's stats and class
    session['char'] = db.execute("SELECT name, hp, mp, map_level FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])
    session['class'] = db.execute("SELECT classes FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

    rowid = db.execute("SELECT rowid FROM characters WHERE user_id = :user_id AND name = :name", user_id = session['user_id'], name = session['list_char'][session['number']]['name'])
    session['rowid'] = rowid[0]['rowid']

    if session['class'][0]["classes"] == "healer":
        session['skill'] = db.execute("SELECT skill_name FROM skills WHERE skill_name = :skill_name", skill_name = "heal")
    else:
        session['skill'] = db.execute("SELECT skill_name FROM skills WHERE skill_name = :skill_name", skill_name = "slash")

    #getting the character's current progress on the map
    map_level = db.execute("SELECT map_level FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

    #remembering where the user's character is currently located
    session["map_level"] = map_level[0]["map_level"]

    #getting the character's replay values
    session['player_replay'] = db.execute("SELECT replay FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

    return render_template("home.html", character=session['char'], char_class=session['class'], skill=session['skill'])

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():

    if request.method == "GET":
        return render_template("create.html", char_created = session['character_created'])
    else:
        if not request.form.get("name") or db.execute("SELECT name FROM characters WHERE name = :name", name = request.form.get("name")):
            return apology("Character name is not valid", 403)

        session['character_created'] = 'yes'

        if request.form.get("name"):
            db.execute("INSERT INTO characters (name, classes, user_id, map_level) VALUES (:name, :classes, :user_id, 1)", name = request.form.get('name'), classes = request.form.get("classes"), user_id = session["user_id"])

            #fix this part, rowid not working
            rowid = db.execute("SELECT rowid FROM characters WHERE user_id = :user_id AND name = :name", user_id = session['user_id'], name = request.form.get('name'))
            session['rowid'] = rowid[0]['rowid']
            db.execute('''INSERT INTO 'monsters' ('name', 'map_level', 'hp', 'sequence', 'monster_set') VALUES
                ('monster1_a', 1, 10, 1, :monster_set),
                ('monster1_b', 1, 10, 2, :monster_set),
                ('monster1_c', 1, 10, 3, :monster_set),
                ('monster2_a', 2, 20, 1, :monster_set),
                ('monster2_b', 2, 20, 2, :monster_set),
                ('monster2_c', 2, 20, 3, :monster_set),
                ('monster3_a', 3, 30, 1, :monster_set),
                ('monster3_b', 3, 30, 2, :monster_set),
                ('monster3_c', 3, 30, 3, :monster_set)
                ''', monster_set = session['rowid'])

        return redirect("/")

@app.route("/finish", methods=["GET", "POST"])
@login_required
def finish():

    if request.method == "POST":

        #add 1 to replay character's replay field
        db.execute("UPDATE characters SET replay = :replay WHERE user_id = :user_id AND name = :name", replay = session['player_replay'][0]['replay'] + 1,  user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

        #getting the character's values for updating
        session['player_replay'] = db.execute("SELECT replay FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

        #default values to use for HP and MP
        player_hp = 50
        player_mp = 30

        #update character's HP and MP by an increment of 5 multiplied by the current number of replays + default value for HP and MP at the very start of the game
        #update map level to 1
        db.execute("UPDATE characters SET hp = :hp, mp = :mp, map_level = :map_level WHERE user_id = :user_id AND name = :name", hp = player_hp + (session['player_replay'][0]['replay']*5), mp = player_mp + (session['player_replay'][0]['replay']*5), map_level = 1, user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

        #default hp values for monsters
        monster1_hp = 10
        monster2_hp = 20
        monster3_hp = 30

        #updating monsters for level 1, 2, and 3
        db.execute("UPDATE monsters SET hp = :hp WHERE map_level = :map_level", hp = monster1_hp + (session['player_replay'][0]['replay']*5), map_level = 1)
        db.execute("UPDATE monsters SET hp = :hp WHERE map_level = :map_level", hp = monster2_hp + (session['player_replay'][0]['replay']*5), map_level = 2)
        db.execute("UPDATE monsters SET hp = :hp WHERE map_level = :map_level", hp = monster3_hp + (session['player_replay'][0]['replay']*5), map_level = 3)

        #send back to home screen and set session finish to no
        return redirect("/")

@app.route("/rest", methods=["GET", "POST"])
@login_required
def rest():
    #to recover hp and mp
    db.execute("UPDATE characters SET hp = :hp, mp = :mp WHERE user_id = :user_id AND name = :name", hp = 50 + (session['player_replay'][0]['replay']*5), mp = 30 + (session['player_replay'][0]['replay']*5), user_id = session["user_id"], name = session['list_char'][session['number']]['name'])
    session['char'] = db.execute("SELECT name, hp, mp FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])
    return render_template("rest.html")

@app.route("/maps", methods=["GET", "POST"])
@login_required
def maps():
    if request.method == "GET":
        return redirect("/level/" + str(session["map_level"]))

@app.route("/level/<n>", methods=["GET", "POST"])
@login_required
def level(n):
    if request.method == "GET":

        #getting the monsters for each level, so this can be displayed on the page
        monster = db.execute("SELECT name, hp FROM monsters WHERE map_level = :level AND monster_set = :monster_set", level = n, monster_set = session['rowid'])
        monsters = []

        for dic in monster:
            monsters.append(list(dic.values()))

        return render_template("level.html", n=n, monsters=monsters)

@app.route("/mon_attack", methods=["GET", "POST"])
@login_required
def mon_attack():

    if request.method == "POST":

        #monster's attack
        mon_attack = int(request.form.get("mon_attack"))

        char_health = db.execute("SELECT hp FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

        #updating char's health
        if mon_attack >= char_health[0]["hp"]:
            db.execute("UPDATE characters SET hp = :hp WHERE user_id = :user_id AND name = :name", hp = 0, user_id = session["user_id"], name = session['list_char'][session['number']]['name'])
            session['char'] = db.execute("SELECT name, hp, mp FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])
        else:
            db.execute("UPDATE characters SET hp = :hp WHERE user_id = :user_id", hp = char_health[0]["hp"] - mon_attack, user_id = session["user_id"])
            session['char'] = db.execute("SELECT name, hp, mp FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

    return redirect("/fight")

@app.route("/fight", methods=["GET", "POST"])
@login_required
def fight():

    sequence = 0

    monster_check = db.execute("SELECT name, hp, sequence FROM monsters WHERE monster_set = :monster_set AND map_level = :level", monster_set = session['rowid'], level = session["map_level"])

    for dic in monster_check:
        if dic['hp'] == 0:
            continue
        else:
            sequence = dic['sequence']
            break

    #logic here needs to be fixed
    if sequence == 0 and session['map_level'] <= 2:
        session["map_level"] = session.get("map_level") + 1
        sequence += 1
        db.execute("UPDATE characters SET map_level = :map_level WHERE user_id = :user_id AND name = :name", map_level = session["map_level"], user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

    #getting correct monster information
    session['monsters_info'] = db.execute("SELECT name, hp, sequence FROM monsters WHERE (map_level = :level AND sequence = :sequence AND monster_set = :monster_set)", level = session["map_level"], sequence = sequence, monster_set = session['rowid'])

    #remembering the current monster's name
    session['monster'] = session['monsters_info'][0]['name']

    if request.method == "POST":

        #getting monster's health to be used in logic below
        mon_health = db.execute("SELECT hp FROM monsters WHERE (map_level = :level AND name = :name AND monster_set = :monster_set)", level = session["map_level"], name = session['monster'], monster_set = session['rowid'])

        #checking what sort of attack the character used: either a regular attack or a skill
        if not request.form.get("char_attack"):

            #character's mana to be used for the code below
            char_mana = db.execute("SELECT mp FROM characters WHERE user_id = :user_id and name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

            #checking what skill is used
            if request.form.get("heal"):

                char_health = db.execute("SELECT hp FROM characters WHERE user_id = :user_id", user_id = session["user_id"])
                heal = int(request.form.get("heal")) * 2
                db.execute("UPDATE characters SET hp = :hp, mp = :mp WHERE user_id = :user_id and name = :name", hp = char_health[0]["hp"] + heal, mp = char_mana[0]["mp"] - 3, user_id = session["user_id"], name = session['list_char'][session['number']]['name'])
                session['char'] = db.execute("SELECT name, hp, mp FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

            elif request.form.get("slash"):

                slash = int(request.form.get("slash")) * 2
                db.execute("UPDATE characters SET mp = :mp WHERE user_id = :user_id and name = :name", mp = char_mana[0]["mp"] - 3, user_id = session["user_id"], name = session['list_char'][session['number']]['name'])
                session['char'] = db.execute("SELECT name, hp, mp FROM characters WHERE user_id = :user_id AND name = :name", user_id = session["user_id"], name = session['list_char'][session['number']]['name'])

                if slash >= mon_health[0]["hp"]:
                    #update monster's health
                    db.execute("UPDATE monsters SET hp = :hp WHERE name = :name AND monster_set = :monster_set", hp = 0, name = session['monster'], monster_set = session['rowid'])
                    session['monsters_info'] = db.execute("SELECT name, hp, sequence FROM monsters WHERE (map_level = :level AND sequence = :sequence AND monster_set = :monster_set)", level = session["map_level"], sequence = sequence, monster_set = session['rowid'])
                else:
                    #update monster's health
                    db.execute("UPDATE monsters SET hp = :hp WHERE name = :name AND monster_set = :monster_set", hp = mon_health[0]["hp"] - slash, name = session['monster'], monster_set = session['rowid'])
                    session['monsters_info'] = db.execute("SELECT name, hp, sequence FROM monsters WHERE (map_level = :level AND sequence = :sequence AND monster_set = :monster_set)", level = session["map_level"], sequence = sequence, monster_set = session['rowid'])
        else:
            char_attack = int(request.form.get("char_attack"))

            #checking if monster has enough health to receive the attack
            if char_attack >= mon_health[0]["hp"]:
                #update monster's health
                db.execute("UPDATE monsters SET hp = :hp WHERE name = :name AND monster_set = :monster_set", hp = 0, name = session['monster'], monster_set = session['rowid'])
                session['monsters_info'] = db.execute("SELECT name, hp, sequence FROM monsters WHERE (map_level = :level AND sequence = :sequence AND monster_set = :monster_monster_set)", level = session["map_level"], sequence = sequence, monster_monster_set = session['rowid'])
            else:
                #update monster's health
                db.execute("UPDATE monsters SET hp = :hp WHERE name = :name AND monster_set = :monster_set", hp = mon_health[0]["hp"] - char_attack, name = session['monster'], monster_set = session['rowid'])
                session['monsters_info'] = db.execute("SELECT name, hp, sequence FROM monsters WHERE map_level = :level AND sequence = :sequence AND monster_set = :monster_set", level = session["map_level"], sequence = sequence, monster_set = session['rowid'])

    return redirect("/battle/" + str(session["map_level"]) + "/" + session['monster'])

@app.route("/battle/<lvl>/<monster>", methods=["GET", "POST"])
@login_required
def battle(lvl, monster):

    return render_template("battle.html", n=lvl, monster=session['monster'], monsters_info=session['monsters_info'], character=session['char'], skill=session['skill'], map_level = session['map_level'])

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/char")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Username is not valid", 400)
        elif db.execute("SELECT username FROM users WHERE username = :username", username = request.form.get("username")):
            return apology("username already exists", 400)
        elif not request.form.get("password") and not request.form.get("confirmation"):
            return apology("please retype your password in the second box", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must be the same", 400)

        username = request.form.get("username")
        password = request.form.get("password")
        password = generate_password_hash(password)

        db.execute("INSERT INTO users ('username', 'hash') VALUES (:username, :password)", username=username, password=password)

        return render_template("register.html")
    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
