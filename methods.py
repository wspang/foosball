"""This script is used to track the MicroController measures over a game of foos.
   When a force measure is hit, it triggers a goal for one team.
   4 Players are input for a game. When 10 goals are scored, it uploads data to BQ.
   **unfortunately, cannot get cloud sql proxy on bootleg linux chromebook :( """

from pyfirmata import Arduino, util  # packages to read microcontroller
import time  # used to set a delay after a goal is scored
import os  # below cmd depends on OS type
from connect import bq_connect, sql_connect
import logging


BQ_TABLE = "foosball.player_stats"
SQL_LOG_TABLE = "gamelogs"

class foos:
    def __init__(self):
        pass
    def game(self, hd, hf, ad, af):  # home and away forward/defense positions.
        """Takes 4 players as input for game (brown, silver, and positions)
        Listens to Arduino and tracks goals for the game.
        Process terminates when first team gets 10 goals"""

        os.system('sudo chmod a+rw /dev/ttyACM0')  # set permission on microcontroller

        try:
            usbconnection = '/dev/ttyACM0'  # USB port read on computer
            board = Arduino(usbconnection)
            it = util.Iterator(board=board)  # iterator thread to avoid data overflow

            # vars to track goals during game.
            home_goals = 0
            hping = 830  # this is the sensor value that triggers goal //recal
            away_goals = 0
            aping = 650  # this is the sensor value that triggers goal //recal
            game_over = 10

            # Enable pin reads for Arduino
            it.start()  # start tracking arduino measures
            home_pin = board.get_pin('a:0:i')  # analog, pin, output 'o' or input 'i'
            home_pin.enable_reporting()
            away_pin = board.get_pin('a:1:i')  # analog, pin, output 'o' or input 'i'
            away_pin.enable_reporting()

            # Now, continuously read measures during game to track goals
            while home_goals < game_over or away_goals < game_over:
                if home_pin.read() == bping:
                    home_goals += 1
                    time.sleep(3)
                if away_pin.read() == sping:
                    away_goals += 1
                    time.sleep(3)

            # Metrics to return for DB upload. Player IDs then scores.
            home_won = True if home_goals > away_goals else False
            output = {"home_defense":hd, "home_offense":hf, "away_defense":ad, "away_offense":af,
                        "home_score":home_goals, "away_score":away_goals, "home_won":home_won}

        except:
            output = {"home_defense": hd, "home_offense": hf, "away_defense": ad, "away_offense": af,
                      "home_score": 10, "away_score": 8, "home_won": 1}

        return output

    def game_log(self, results):
        """Take stats from the game and upload to game log table(s)."""
        cols, vals = "", ""
        for k, v in results.items():
            cols += "{}, ".format(k)
            vals += "'{}', ".format(v)
        cols, vals = cols[:-2], vals[:-2]  # drop off last comma
        # Upload results to CloudSQL
        conn = sql_connect()
        with conn.cursor() as cursor:
            sql_query = "INSERT INTO {} ({}) VALUES ({});".format(SQL_LOG_TABLE, cols, vals)
            cursor.execute(sql_query)
            logging.info("executed query: {}".format(sql_query))
            #cursor.commit()
            cursor.close()
        conn.close()
        return "updated."

    def player_stats(self, params):
        """Takes in stats returned from game. Processes for update query to player stats table."""
        # Connect with BQ and update values for player stats by first doing a query on
        # their stats. Then doing a += or some alteration.

        # 1) Parse output of game for player IDs to update whether they won or not.
        if params['home_won'] is True:
            winner_offense = {"player_id":params['home_offense'], "goals_for":params['home_score'],
                "goals_against":params['away_score'], "won":1}
            winner_defense = {"player_id":params['home_defense'], "goals_for":params['home_score'],
                "goals_against":params['away_score'], "won":1}
            loser_offense = {"player_id":params['away_offense'], "goals_for":params['away_score'],
                "goals_against":params['home_score'], "won":0}
            loser_defense = {"player_id":params['away_defense'], "goals_for":params['away_score'],
                "goals_against":params['home_score'], "won":0}
        else:
            winner_offense = {"player_id":params['away_offense'], "goals_for":params['away_score'],
                "goals_against":params['home_score'], "won":1}
            winner_defense = {"player_id":params['away_defense'], "goals_for":params['away_score'],
                "goals_against":params['home_score'], "won":1}
            loser_offense = {"player_id":params['home_offense'], "goals_for":params['home_score'],
                "goals_against":params['away_score'], "won":0}
            loser_defense = {"player_id":params['home_defense'], "goals_for":params['home_score'],
                "goals_against":params['away_score'], "won":0}
        # Create a dictionary of dictionary values to reference for query updates
        gameplayers = {winner_offense['player_id']:winner_offense, winner_defense['player_id']:winner_defense,
                        loser_offense['player_id']:loser_offense, loser_defense['player_id']:loser_defense}

        # 2) Get query of 4 players above to build on their existing values. Returns list.
        with bq_connect() as client:
            condition = "player_id = '{}' or player_id = '{}' or player_id = '{}' or player_id = '{}'".format(
                        winner_offense['player_id'], winner_defense['player_id'], loser_offense['player_id'], loser_defense['player_id'])
            query = "SELECT * EXCEPT name FROM {} WHERE {} ORDER BY player_id".format(BQ_TABLE, condition)
            bq_players = client.query(query)
            bq_players = bq_players.result()  # list of 4 players and their stats.

        # 3) perform 4 update queries on the above players. Below list is player IDs.
        # Need to create a query string to perform one update statement per player.
        player_updates = [winner_offense, winner_defense, loser_offense, loser_defense]
        for pid in bq_players:
            metrics = gameplayers[pid.player_id]  # match BQ player ID to gameplayer stats dict
            gfor, gaga, wins = pid.team_goals_scored + metrics['goals_for'], pid.team_goals_against + metrics['goals_against'], pid.games_won + metrics['won']
            query = ("UPDATE {} SET team_goals_scored = {}, team_goals_against = {}, games_won = {} " 
                     "WHERE player_id = '{}'").format(BQTABLE, gfor, gaga, wins, pid.player_id)
            with bq_connect() as client:
                client.query(query)
        return "successfully updated stats"
