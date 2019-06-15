"""Main file that will be used to navigate the foosball stats tracking app. 
   Main methods are called from methods file. 
   Utilizes a CloudSQL backend for stats tracking. For now, only have player entry page."""

from flask import Flask, redirect, render_template, request
from connect import bq_connect
from methods import Foos, GameSetup
app = Flask(__name__)

# Establish connections to Cloud SQL and provide service acct key for client access.
GOOGLE_APPLICATION_CREDENTIALS, CONNECTION = "cloudsql_key.json", bq_connect()  

#    output = {"home_defense":hd, "home_offense":hf, "away_defense":ad, "away_offense":af, 
 #               "home_score":home_goals, "away_score":away_goals, "home_won":home_won}

@app.route('/')
def main_page():
    """This function allows a user to navigate to either a start game page
       or a stats viewing page"""
    return "wats pippin"


@app.route('/getplayer/<p>', methods=['GET'])
def getplayer(p):
    # check if player exists already. if so, return name.
    ds_ent = GameSetup().ds_check(pid=p)
    if ds_ent is not False:
        return ds_ent
    else:  # player does not exist, so need to prompt for entry.
        return False


@app.route('/addplayer', methods=['POST'])
def addplayer():
    """If a player does not already exist, post API is made to create a player with ID and name.
       Player info is logged in DataStore and Cloud SQL player stats table."""
    info = request.get_json(silent=True)  # get api body of id and name
    pid, name = info['pid'], info['fullName']
    GameSetup().player_entry(pid=pid, name=name)  # make update to Datastore and Cloud SQL
    return pid


@app.route('/gamelog', methods=['POST'])
def game():
    """The game_init file will run the game or supply user input for stats.
       Those stats are formatted in json and read here to log in game log DB."""
    game_results = request.get_json(silent=True)  # get json from post api to process.
    logged = Foos().game_log(results=game_results)  # Log the game in game logging table.
    return logged

@app.route('/playerstats', methods=['POST'])
def stats():
    """The game_init file will run the game or supply user input for stats.
       Those stats are formatted in json and read here to log in player stats DB."""
    game_results = request.get_json(silent=True)
    logged = Foos().player_stats(params=game_results)
    return logged

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
