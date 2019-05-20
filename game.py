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

def test():
    """simple test function to see if Arduino can read force sensors"""
    # establish pins and enable reporting
    it.start()
    brown_pin = board.get_pin('a:0:i')  # analog, pin, output 'o' or input 'i'
    brown_pin.enable_reporting()
    silver_pin = board.get_pin('a:1:i')  # analog, pin, output 'o' or input 'i'    
    silver_pin.enable_reporting()    

    for n in range(100):  # just loop through n reads
        print("Brown measure: {0}\nSilver measure: {1}".format(
            brown_pin.read(), silver_pin.read()))
        #time.sleep(1)  # set some delay for sensor read
    return

def game():
    """Takes 4 players as input for game (brown, silver, and positions)
    Listens to Arduino and tracks goals for the game.
    Process terminates when first team gets 10 goals"""

    #Input players via cmd line input
    bd = str(raw_input("\nBrown Defense ID:\n\t--"))
    bf = str(raw_input("\nBrown Offense ID:\n\t--"))
    sd = str(raw_input("\nSilver Defense ID:\n\t--"))
    sf = str(raw_input("\nSilver Offense ID:\n\t--"))

    # vars to track goals during game.
    brown_goals = 0
    bping = 830  # this is the sensor value that triggers goal //recal
    silver_goals = 0
    sping = 650  # this is the sensor value that triggers goal //recal
    game_over = 10
    
    it.start()  # start tracking arduino measures 
    brown_pin = board.get_pin('a:0:i')  # analog, pin, output 'o' or input 'i'
    brown_pin.enable_reporting()
    silver_pin = board.get_pin('a:1:i')  # analog, pin, output 'o' or input 'i'    
    silver_pin.enable_reporting()    

    # Now, continuously read measures during game to track goals
    while brown_goals < game_over or silver_goals < game_over:
        if brown_pin.read() == bping:
            brown_goals += 1
            time.sleep(3)
        if silver_pin.read() == sping:
            silver_goals += 1
            time.sleep(3)

    winners = (bd,bf) if brown_goals > silver_goals else (sd,sf)
    print "{0} and {1} win!".format(winners[0], winners[1])

    # need to write to DB the winners and scores, use CLoud SQL for now?
    return

test()
#game()