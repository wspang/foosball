"""This script is used to track the MicroController measures over a game of foos.
   When a force measure is hit, it triggers a goal for one team. 
   4 Players are input for a game. When 10 goals are scored, it uploads data to SQL."""

from pyfirmata import Arduino, util  # packages to read microcontroller
import time  # used to set a delay after a goal is scored 
import os

os.system('sudo chmod a+rw /dev/ttyACM0')  # set permission on microcontroller


usbconnection = '/dev/ttyACM0'  # USB port read on computer 
board = Arduino(usbconnection)
it = util.Iterator(board=board)  # iterator thread to avoid data overflow

def game(hd, hf, ad, af):  # home and away forward/defense positions.
    """Takes 4 players as input for game (brown, silver, and positions)
    Listens to Arduino and tracks goals for the game.
    Process terminates when first team gets 10 goals"""

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

    # Metrics to return for DB upload
    home_won = True if home_goals > away_goals else False
    output = {"home_defense":hd, "home_offense":hf, "away_defense":ad, "away_offense":af, 
                "home_score":home_goals, "away_score":away_goals, "home_won":home_won}
    return output

def player_stats(params: dict):
    """Takes in stats returned from game. Processes for update query to player stats table."""
    
