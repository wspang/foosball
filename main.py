"""Main file that will be used to navigate the foosball stats tracking app. 
   Main methods are called from methods file. 
   Utilizes a CloudSQL backend for stats tracking. For now, only have player entry page."""

from flask import Flask, redirect, render_template
from connect import bq_connect
from methods import game,player_stats
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

@app.route('/game')
def game():
    """Calls on game method from methods file. Allow player name entry then start game."""
    results = game(hd=a,hf=b,ad=c,af=d)  # Call game method and get results
    
    # define columns and values to insert into main table. format query string.   
    cols, vals = "", ""
    for k, v in results.items():
        cols += "{}, ".format(k)
        vals += "{}, ".format(v)
    cols, vals = cols[:-2], vals[:-2]  # drop off last comma

    # Upload results to CloudSQL
    with CONNECTION.cursor() as cursor:
        sql_query = "INSERT INTO TABLE main({}) VALUES ({});".format(cols, vals)
        cursor.execute(sql_query)
        cursor.commit()
        cursor.close()
    CONNECTION.close()
    return

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
