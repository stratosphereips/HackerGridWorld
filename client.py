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
import emoji


__version__ = 'v0.1'


def start_client(server, port, w):
    """
    Start the socket server
    Define the function to deal with data
    """
    try:

        logger = logging.getLogger('CLIENT')
        logger.info('Starting client')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server, port))

        while True:
            # Get data
            net_data = sock.recv(2048)
            logger.info(f'Received: {net_data.decode()!r}')

            key = process_data(net_data, w)

            if "KEY_UP" in key:
                sock.send(b'UP')
            elif "KEY_DOWN" in key:
                sock.send(b'DOWN')
            elif "KEY_RIGHT" in key:
                sock.send(b'RIGHT')
            elif "KEY_LEFT" in key:
                sock.send(b'LEFT')
            elif "q" in key:
                break
            else:
                key = ''
                sock.send(b' ')
            logger.info(f'Sending: {key!r}')


        sock.close()
    except Exception as e:
        logging.error(f'Error in start_client: {e}')

def process_data(data, w):
    """
    Process the data sent by the server
    """
    try:
        # convert to dict
        data = json.loads(data)
        size_x = int(data['size'].split('x')[0])
        size_y = int(data['size'].split('x')[1])
        world_score = data['score']
        world_positions = data['positions']
      
        # Print positions
        minimum_y = 10
        for x in range(size_x):
            for y in range(size_y):
                w.addstr(y + minimum_y, x, emoji.emojize(str(world_positions[x + (y * 10)])))
        # Print score
        w.addstr(minimum_y + size_y + 1, 0, f'Score: {str(world_score):>5}') 

        # Get a key
        key = w.getkey()
        w.addstr(size_y + minimum_y + 2, 0, f'{key:<15}')
        w.refresh()
        return key

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
    logging.basicConfig(filename='client.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',level=logging.INFO)
    logging.info('Client started')


    try:
        curses.wrapper(curses_main)
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        logging.debug('Goodbye')