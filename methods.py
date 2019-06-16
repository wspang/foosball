"""This script is used to track the MicroController measures over a game of foos.
   When a force measure is hit, it triggers a goal for one team.
   4 Players are input for a game. When 10 goals are scored, it uploads data to BQ.
   **unfortunately, cannot get cloud sql proxy on bootleg linux chromebook :( """

import time  # used to set a delay after a goal is scored
import os  # below cmd depends on OS type
from connect import sql_connect, ds_connect
import logging
from google.cloud import datastore


class GameSetup:
    def __init__(self):
        self.client, self.kind, self.sql_players = ds_connect(), "TredenceEmployees", "players"
        pass

    def ds_check(self, pid):
        """Get from Datastore to see if entity exists."""
        # Establish client connection then get player name from DataStore.
        get_key = self.client.key(self.kind, pid)

        try:  # If return, the name / entry exists.
            name = dict(self.client.get(get_key))['fullName']
            return name
        except TypeError:  # Type error means player does not exist. Need to make.
            return False

    def player_entry(self, pid, name):
        """If an entry does not exist -- have player make an entry and update
           DataStore contact log and insert row to Cloud SQL."""
        # 1) Create a DataStore entity in the player kind
        key = self.client.key(self.kind, pid)
        entity = datastore.Entity(key=key)
        entity['fullName'] = name
        self.client.put(entity)
        logging.info("Created datastore entity {}-{}".format(pid, name))

        # 2) Insert a player_id row to the cloud sql table.
        insert_query = "INSERT INTO {0} VALUES ('{1}', '{2}', {3}, {3}, {3}, {3}, {3}, {3}, {3}, {3});".format(
            self.sql_players, pid, name, 0)
        conn = sql_connect()
        with conn.cursor() as cur:
            cur.execute(insert_query)
            cur.close()
        conn.close()
        logging.info("Inserted {} into sql as player id: {}".format(name, pid))
        return True


class Foos:
    def __init__(self):
        self.sql_logs, self.sql_players = "gamelogs", "players"
        pass

    def game_log(self, results):
        """Take stats from the game and upload to game log table(s)."""
        # 1) Format results json keys into column inserts string for SQL query.
        #       Format values into query string as either ints or 'strings'
        cols, vals = "", ""
        for k, v in results.items():
            cols += "{}, ".format(k)
            if type(v) == int:
                vals += "{}, ".format(v)
            else:
                vals += "'{}', ".format(v)
        cols, vals = cols[:-2], vals[:-2]  # drop off last comma and space.

        # Upload results to CloudSQL
        conn = sql_connect()
        with conn.cursor() as cursor:
            sql_query = "INSERT INTO {} ({}) VALUES ({});".format(self.sql_logs, cols, vals)
            cursor.execute(sql_query)
            logging.info("executed query: {}".format(sql_query))
            cursor.close()
        conn.close()
        return True

    def player_stats(self, params):
        """Takes in stats returned from game. Processes for update query to player stats table."""
        # Parse game results and format a query for each player dependent on their team outcome.

        # 1) Parse output of game for player IDs to update whether they won or not. Will use as vals in update query.
        if params['home_won'] == 1:  # make values for home as winners
            winner_offense = {"player_id": params['home_offense'], "goals_for": params['home_score'],
                              "goals_against": params['away_score'], "won": 1, "offense_games": 1, "defense_games": 0}
            winner_defense = {"player_id": params['home_defense'], "goals_for": params['home_score'],
                              "goals_against": params['away_score'], "won": 1, "defense_games": 1, "offense_games": 0}
            loser_offense = {"player_id": params['away_offense'], "goals_for": params['away_score'],
                             "goals_against": params['home_score'], "won": 0, "offense_games": 1, "defense_games": 0}
            loser_defense = {"player_id": params['away_defense'], "goals_for": params['away_score'],
                             "goals_against": params['home_score'], "won": 0, "defense_games": 1, "offense_games": 0}
        else:  # make values for away as winners
            winner_offense = {"player_id": params['away_offense'], "goals_for": params['away_score'],
                              "goals_against": params['home_score'], "won": 1, "offense_games": 1, "defense_games": 0}
            winner_defense = {"player_id": params['away_defense'], "goals_for": params['away_score'],
                              "goals_against": params['home_score'], "won": 1, "defense_games": 1, "offense_games": 0}
            loser_offense = {"player_id": params['home_offense'], "goals_for": params['home_score'],
                             "goals_against": params['away_score'], "won": 0, "offense_games": 1, "defense_games": 0}
            loser_defense = {"player_id": params['home_defense'], "goals_for": params['home_score'],
                             "goals_against": params['away_score'], "won": 0, "defense_games": 1, "offense_games": 0}

        # Create a dictionary of dictionary values to reference for query updates
        gameplayers = {winner_offense['player_id']:winner_offense, winner_defense['player_id']:winner_defense,
                        loser_offense['player_id']:loser_offense, loser_defense['player_id']:loser_defense}
        logging.info("game input:{}".format(gameplayers))

        # 2) Get query of 4 players above to build on their existing values. Returns list.
        conn = sql_connect()
        #   a) only retrieve records for the 4 players
        condition = "player_id = '{}' or player_id = '{}' or player_id = '{}' or player_id = '{}'".format(
                    winner_offense['player_id'], winner_defense['player_id'], loser_offense['player_id'],
                        loser_defense['player_id'])
        get_cols = ("player_id, total_games, total_wins, offense_games, offense_wins, defense_games, defense_wins, "
                    "team_goals_scored, team_goals_against")
        query = "SELECT {} FROM {} WHERE {};".format(get_cols, self.sql_players, condition)
        with conn.cursor() as cur:
            cur.execute(query)
            old_stats = cur.fetchall()  # list of 4 players and their stats.
            cur.close()
        conn.close()
        logging.info("old stats: {}".format(old_stats))

        # 3) With four players retrieved above, iterate through to get new values. Then perform update query.
        for pstats in old_stats:
            # Use metrics and query values to assign new stats values
            metrics = gameplayers[pstats[0]]  # json of game results corresponding to current player in loop from query
            player_id, total_games, total_wins = pstats[0], pstats[1] + 1, pstats[2] + metrics['won']
            offense_games = pstats[3] + metrics['offense_games']
            offense_wins = pstats[4] + metrics['won'] if metrics['offense_games'] == 1 else pstats[4]
            defense_games = pstats[5] + metrics['defense_games']
            defense_wins = pstats[6] + metrics['won'] if metrics['defense_games'] == 1 else pstats[6]
            team_goals_scored,team_goals_against = pstats[7] + metrics['goals_for'],pstats[8] + metrics['goals_against']

            # Perform an update query on SQL table with given values above.
            update_query = ("UPDATE {} SET "
                            "total_games = {}, total_wins = {}, "
                            "offense_games = {}, offense_wins = {}, "
                            "defense_games = {}, defense_wins = {}, "
                            "team_goals_scored = {}, team_goals_against = {} "
                            "WHERE player_id = '{}';").format(self.sql_players, total_games, total_wins,
                                                           offense_games, offense_wins, defense_games,
                                                           defense_wins, team_goals_scored,
                                                           team_goals_against, player_id)

            logging.info("player stats update query: {}".format(update_query))
            conn = sql_connect()
            with conn.cursor() as cur:
                cur.execute(update_query)
                cur.close()
            conn.close()
        return True
