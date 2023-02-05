#!/usr/bin/env python
# Client for humans for the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023

import argparse
from datetime import datetime
import logging
import json
import curses
import socket
import time

# Init the curses screen
#stdscr = curses.initscr()
# Dont show the pressed keys in screen
#curses.noecho()
# Dont wait for enter
#curses.cbreak()
# Let curses take care of special keys as RIGHTARROW
#stdscr.keypad(True)
#stdscr.addstr(20, 20, "11111")
#stdscr.refresh()


__version__ = 'v0.1'

def start_client(server, port, w):
    """
    Start the socket server
    Define the function to deal with data
    """
    logger = logging.getLogger('CLIENT')
    logger.info('Starting client')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, port))

    while True:
        # Get data
        data = sock.recv(1024)
        logger.info(f'Received: {data.decode()!r}')

        process_data(data, w)

        # Send back
        message = b'hi'
        sock.send(message)
        logger.info(f'Sending: {message!r}')
        time.sleep(1)

    sock.close()

def process_data(data, w):
    """
    Process the data sent by the server
    """
    try:
        # convert to dict
        data = json.loads(data)
        size_x = int(data['size'].split('x')[0])
        size_y = int(data['size'].split('x')[1])
        world = data['positions']
        len_world = len(world)
      
        minimum_y = 3
        for x in range(3):
            for y in range(3):
                #w.addstr(y + minimum_y, x, str(world[x + (y * 10)]))
                #w.addstr(y + minimum_y, x, str('X'))
                w.addstr(y, x, str('X'))
                w.refresh()

        # Get a key
        #w.getch()
    except Exception as e:
        logging.error(f'Error in process_data: {e}')


def curses_main(w):

    """
    This function is called curses_main to emphasise that it is
    the logical if not actual main function, called by curses.wrapper.

    Its purpose is to call several other functions to demonstrate
    some of the functionality of curses.
    """

    w.addstr("---------------------\n")
    w.addstr("| Hacker Grid World |\n")
    w.addstr("---------------------\n")
    w.refresh()

    start_client('127.0.0.1', 9000, w)

    #w.addstr("\npress any key to exit...")
    #w.refresh()
    #w.getch()



def moving_and_sleeping(w):
    """
    Demonstrates moving the cursor to a specified position before printing,
    and sleeping for a specified period of time.
    These are useful for very basic animations.
    """
    row = 5
    col = 0

    curses.curs_set(False)

    for c in range(65, 91):
        w.addstr(row, col, chr(c))
        w.refresh()
        row += 1
        col += 1
        curses.napms(100)

    curses.curs_set(True)
    w.addch('\n')


def colouring(w):
    """
    Demonstration of setting background and foreground colours.
    """
    if curses.has_colors():
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_CYAN)

        w.addstr("Yellow on red\n\n", curses.color_pair(1))
        w.refresh()

        w.addstr("Green on green + bold\n\n", curses.color_pair(2) | curses.A_BOLD)
        w.refresh()

        w.addstr("Magenta on cyan\n", curses.color_pair(3))
        w.refresh()

    else:
        w.addstr("has_colors() = False\n");
        w.refresh()


# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Client for humans of th Hacker Grid World Server. Version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Amount of verbosity. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Amount of debugging. This shows inner information about the flows.', action='store', required=False, type=int)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s',)
    logging.info('Client started')


    try:
        curses.wrapper(curses_main)
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        logging.debug('Goodbye')