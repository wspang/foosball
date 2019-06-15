"""A local script is needed to connect with the Arduino Uno on a local device.
   Because of a local device dependency for tracking, this script will initiate
   the game, log players, and track metrics. APIs will then be made to the FoosBall app hosted
   on GCP App Engine which will log statistics.

   Flow:: 1) Set up players for the game by entering employee ID.
            either makes a new player or verifies existing one by checking DataStore entry.
          2) Initiate the game. Players can choose to either use sensors or manually input their metrics.
          3) Make API Calls to the Foos app to log stats in Cloud SQL."""

from pyfirmata import Arduino, util  # packages to read microcontroller
import os
import sys
import requests
import time
URL = "https://foosball-dot-cpb100-213205.appspot.com/{}"

def get_players():
    """Players enter their employee IDs to log them to game.
       Checks DataStore to see if contact exists or not. If not, user enters their name.
       If so, will show their name as a confirmation."""
    # Command line inputs to player IDs.
    hf = str(input("\nHOME OFFENSE:\n\tenter 4 digit employee ID:"))
    hd = str(input("\nHOME DEFENSE:\n\tenter 4 digit employee ID:"))
    af = str(input("\nAWAY OFFENSE:\n\tenter 4 digit employee ID:"))
    ad = str(input("\nAWAY DEFENSE:\n\tenter 4 digit employee ID:"))
    # Check if player entry exists. If not, create one. If so, confirm name.
    for p in [hf, hd, af, ad]:

        if len(p) != 4:  # check first if they entered a valid id.
            raise Exception("{} did not enter a valid 4 digit ID. Do it again.".format(p))

        purl = URL.format("getplayer/{}").format(p)
        player = requests.get(url=purl)
        print("player API:", player.status_code, player.text)
        player = player.text

        if player != "noPlayer":  # player exists
            print("game on {}".format(player))

        else:  # player does not exist, need to make an entry
            purl = URL.format("addplayer")
            body = {"pid": p, "fullName": str(input("emp {}: enter your name".format(p)))}
            requests.post(url=purl, json=body)

    return [hf, hd, af, ad]  # return a list of player IDs to start game.


def sensor_game(hf, hd, af, ad):  # home and away forward/defense positions.
    """Takes 4 players as input for game (brown, silver, and positions)
    Listens to Arduino and tracks goals for the game.
    Process terminates when first team gets 10 goals"""

    os.system('sudo chmod a+rw /dev/ttyACM0')  # set permission on microcontroller


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
    output = {"home_defense": hd, "home_offense": hf, "away_defense": ad, "away_offense": af,
              "home_score": home_goals, "away_score": away_goals, "home_won": home_won}

    return output


def input_game(hf, hd, af, ad):
    """If sensor is bugging out or don't feel like using it - can also enter game stats manually."""
    while True:
        try:
            hscore = int(input("\nEnter the score for home team:"))
            ascore = int(input("\nEnter the score for away team:"))
        except TypeError:
            print("Need to enter an integer between 0 and 10")
            continue
        if hscore > 10 or ascore > 10:
            print("Need to enter an integer between 0 and 10")
            continue
        break

    res = 1 if hscore > ascore else 0
    output = {"home_defense": hd, "home_offense": hf, "away_defense": ad, "away_offense": af,
              "home_score": hscore, "away_score": ascore, "home_won": res}
    return output

def upload_data(results):
    """Takes game results from above and makes API calls to foos app to load in stats."""
    requests.post(url=URL.format("gamelog"), json=results)
    requests.post(url=URL.format("playerstats"), json=results)
    return True

# test above.
#print("testing get players:", get_players())



# Execute the above flow of functions to run process.
"""players = get_players()  # returns list of entry for game function
try:
    if sys.argv[1] == 's':
        results = sensor_game(hf=players[0], hd=players[1], af=players[2], ad=players[3])
    else:
        results = input_game(hf=players[0], hd=players[1], af=players[2], ad=players[3])
except IndexError:
    results = input_game(hf=players[0], hd=players[1], af=players[2], ad=players[3])
upload_data(results=results)"""