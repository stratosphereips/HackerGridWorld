#!/usr/bin/env python
# Client for humans for the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023

import argparse
import logging
import json
import curses
import socket
import emoji


__version__ = 'v0.1'

class Game():
    """
    Game object
    """
    def __init__(self):
        pass

def start_client(w, sock):
    """
    Start the socket server
    Define the function to deal with data
    """
    try:

        logger = logging.getLogger('CLIENT')
        logger.info('Starting client')

        myworld = Game()

        while True:
            # Get data
            net_data = sock.recv(2048)
            logger.info(f'Received: {net_data.decode()!r}')

            # Process data, print world
            process_data(myworld, net_data, w)

            # Check end
            if check_end(myworld):
                # The game ended
                # Get the new map to reset
                net_data = sock.recv(2048)
                logger.info(f'Received: {net_data.decode()!r}')
                # Process data, print world
                process_data(myworld, net_data, w)

            # Get key from user and process it
            key = get_key(myworld, w)

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


    except Exception as e:
        logging.error(f'Error in start_client: {e}')


def check_end(myworld):
    """
    Check if we reached the end
    """
    if myworld.end:
        # Game end
        logging.info(f'Game ended: Score: {myworld.world_score}')
        return True

def process_data(myworld, data, w):
    """
    Process the data sent by the server
    """
    try:
        # convert to dict
        data = json.loads(data)
        myworld.size_x = int(data['size'].split('x')[0])
        myworld.size_y = int(data['size'].split('x')[1])
        myworld.world_score = data['score']
        myworld.world_positions = data['positions']
        myworld.end = data['end']

        # Print positions
        minimum_y = 10
        for x in range(myworld.size_x):
            for y in range(myworld.size_y):
                w.addstr(y + minimum_y, x, emoji.emojize(str(myworld.world_positions[x + (y * 10)])))
        # Print score
        w.addstr(minimum_y + myworld.size_y + 1, 0, f"Score: {str(myworld.world_score):>5}")
    except Exception as e:
        logging.error(f'Error in process_data: {e}')

def get_key(myworld, w):
    """
    Get a key from the user
    """
    minimum_y = 10
    # Get a key
    key = w.getkey()
    w.addstr(myworld.size_y + minimum_y + 2, 0, f'{key:<15}')
    w.refresh()
    return key


def main(w):
    """
    This function is called curses_main to emphasise that it is
    the logical if not actual main function, called by curses.wrapper.

    Its purpose is to call several other functions to demonstrate
    some of the functionality of curses.

    w is the curses window
    """

    # Print the banner
    w.addstr("---------------------\n")
    w.addstr("| Hacker Grid World |\n")
    w.addstr("---------------------\n")
    w.refresh()

    # Get the socket of communication
    server = args.server
    port = args.port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, port))

    # Start the client
    start_client(w, sock)

    sock.close()


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
        w.addstr("has_colors() = False\n")
        w.refresh()


# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Client for humans of the Hacker Grid World Server. Version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Verbosity level. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Debugging level. This shows more information about the flows.', action='store', required=False, type=int)
    parser.add_argument('-s', '--server', help='IP address of game server.', action='store', required=False, type=str, default='127.0.0.1')
    parser.add_argument('-p', '--port', help='Port of game server.', action='store', required=False, type=int, default=9000)

    args = parser.parse_args()
    logging.basicConfig(filename='client.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',level=logging.INFO)
    logging.info('Client started')

    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        logging.debug('Terminating by KeyboardInterrupt')
        raise SystemExit
    except Exception as e:
        logging.error(f'Exception in __main__: {e}')
    finally:
        logging.debug('Goodbye')
