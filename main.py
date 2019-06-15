"""Main file that will be used to navigate the foosball stats tracking app. 
   Main methods are called from methods file. 
   Utilizes a CloudSQL backend for stats tracking. For now, only have player entry page."""

from flask import Flask, redirect, render_template, request
from connect import bq_connect
from methods import foos
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

@app.route('/game', methods=['POST'])
def game():
    """Calls on game method from methods file. Allow player name entry then start game."""
    #results = foos().game(hd='0001',hf='0002',ad='0003',af='0004')  # Call game method and get results

    hd,hf,ad,af =  '0001', '0002', '0003', '0004'

    output = {"home_defense": hd, "home_offense": hf, "away_defense": ad, "away_offense": af,
              "home_score": 10, "away_score": 8, "home_won": 1}

    logged = foos().game_log(results=output)  # Log the game in game logging table.
    #players_logged = foos().player_stats(params=results)  # update individual player stats.
    return logged

@app.route('/stats')
def stats():
    """Allow users to check stats on previous games. Will eventually throw in fancy filters"""
    with CONNECTION.cursor() as cursor:
        sql_query = ''
        cursor.execute(sql_query)
        cursor.commit()
    CONNECTION.close()
    return

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
