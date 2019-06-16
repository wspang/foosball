"""A local script is needed to connect with the Arduino Uno on a local device.
   Because of a local device dependency for tracking, this script will initiate
   the game, log players, and track metrics. APIs will then be made to the FoosBall app hosted
   on GCP App Engine which will log statistics.

   Flow:: 1) Set up players for the game by entering employee ID.
            either makes a new player or verifies existing one by checking DataStore entry.
          2) Initiate the game. Players can choose to either use sensors or manually input their metrics.
          3) Make API Calls to the Foos app to log stats in Cloud SQL.

    @Author: Will Spangler"""

# from pyfirmata import Arduino, util  # packages to read microcontroller
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
    hf = str(input("\nHOME OFFENSE:\n\tenter 4 digit employee ID:\n\t"))
    hd = str(input("\nHOME DEFENSE:\n\tenter 4 digit employee ID:\n\t"))
    af = str(input("\nAWAY OFFENSE:\n\tenter 4 digit employee ID:\n\t"))
    ad = str(input("\nAWAY DEFENSE:\n\tenter 4 digit employee ID:\n\t"))

    # Check if ID entered is valid 4 numeric characters.
    for p in [hf, hd, af, ad]:
        if len(p) != 4:  # check first if they entered a valid id.
            raise Exception("{} did not enter a valid 4 digit numeric ID. Do it again.".format(p))
        try:  # check if ID entered is 4 numeric character.
            int(p)
        except ValueError:
            raise Exception("{} did not enter a valid 4 digit numeric ID. Do it again.".format(p))

    # If here, IDs are valid. Now make API requests to see if there is an existing record.
    for p in [hf, hd, af, ad]:
        purl = URL.format("getplayer/{}").format(p)
        player = requests.get(url=purl)
        print("player API:", player.status_code, player.text)
        player = player.text

        # If player exists, print name and good to go.
        if player != "noPlayer":  # player exists
            print("game on {}".format(player))

        # Need to make additional API Call if player does not exist to create entry.
        else:
            purl = URL.format("addplayer")
            body = {"pid": p, "fullName": str(input("emp {}: enter your name\n\t".format(p)))}
            requests.post(url=purl, json=body)

    return [hf, hd, af, ad]  # return a list of player IDs to start game.


def input_game(hf, hd, af, ad):
    """If sensor is bugging out or don't feel like using it - can also enter game stats manually."""
    # Continuously loop through to have player input scores until scores are valid (pass tests)
    while True:
        try:
            hscore = int(input("\nEnter the score for home team:\n\t"))
            ascore = int(input("\nEnter the score for away team:\n\t"))
        except ValueError:
            print("Need to enter an integer between 0 and 10")
            continue
        if hscore > 10 or ascore > 10:
            print("Need to enter an integer between 0 and 10")
            continue
        elif hscore != 10 and ascore != 10:
            print("For game to be over a team needs 10 goals. Try again.")
            continue
        break

    # Determine game result and return json for game logs.
    res = 1 if hscore > ascore else 0
    output = {"home_defense": hd, "home_offense": hf, "away_defense": ad, "away_offense": af,
              "home_score": hscore, "away_score": ascore, "home_won": res}
    print("game output:\n{}".format(output))
    return output

def upload_data(results):
    """Takes game results from above and makes API calls to foos app to load in stats."""
    print("calling Gamelog API")
    gl = requests.post(url=URL.format("gamelog"), json=results)
    print("Gamelog API status: {}\n\nCalling Player stats API".format(gl.status_code))
    ps = requests.post(url=URL.format("playerstats"), json=results)
    print("Called player stats API with status: {}".format(ps.status_code))
    return True


"""def sensor_game(hf, hd, af, ad):  # home and away forward/defense positions.
    #Takes 4 players as input for game (brown, silver, and positions)
    #Listens to Arduino and tracks goals for the game.
    #Process terminates when first team gets 10 goals

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
    home_won = 1 if home_goals > away_goals else 0
    output = {"home_defense": hd, "home_offense": hf, "away_defense": ad, "away_offense": af,
              "home_score": home_goals, "away_score": away_goals, "home_won": home_won}

    return output

# Execute the above flow of functions to run process.
if __name__ == '__main__':
    # 1) Get players
    players = get_players()
    # 2) Determine game monitoring as either sensors or user input.
    try:
        if sys.argv[1][0] == 's':
            results = sensor_game(hf=players[0], hd=players[1], af=players[2], ad=players[3])
        else:
            results = input_game(hf=players[0], hd=players[1], af=players[2], ad=players[3])
    except IndexError:
        results = input_game(hf=players[0], hd=players[1], af=players[2], ad=players[3])
    # Upload game logs to Cloud SQL table and update player stats table.
    upload_data(results=results)"""

if __name__ == '__main__':
    # 1) get player IDs. create new if needed.
    players = get_players()
    # 2) Use input for game outcome.
    results = input_game(hf=players[0], hd=players[1], af=players[2], ad=players[3])
    # 3) Update Cloud SQL tables with game metrics.
    upload_data(results=results)
