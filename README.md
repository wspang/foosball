# foosball
Foosball metrics logging app that is hosted on GCP App Engine. Utilizes Cloud DataStore to track Player_IDs and names. Utilizes Cloud SQL for two tables:

  gamelogs: uploads every game record with a datetime stamp recording who played which position, what the score was, and who won.
  
  players: Every row belongs to a player (player_id). Tracks how many games they have played and won overall, on offense, and defense.
  
Users can easily input game logs from their terminal by running `python game_init.py`. They will then be prompted from the cmd line to enter their player IDs, make a new profile if necessary, and enter the game results. Multiple APIs are made in this script to log info on GCP.

Holding off on force sensors for now, just using player input. Maybe build a webapp for input in the future.
