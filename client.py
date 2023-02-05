#!/usr/bin/env python
# Client for humans for the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023

import argparse
from datetime import datetime
import logging
import json
import asyncio
import curses

# Init the curses screen
stdscr = curses.initscr()
# Dont show the pressed keys in screen
#curses.noecho()
# Dont wait for enter
#curses.cbreak()
# Let curses take care of special keys as RIGHTARROW
#stdscr.keypad(True)
#stdscr.addstr(0, 0, 'HI THERE')
#stdscr.refresh()
stdscr.addstr(20, 20, "11111")
stdscr.refresh()


__version__ = 'v0.1'

async def client(server, port):
    """
    Start the socket server
    Define the function to deal with data
    """
    logger = logging.getLogger('CLIENT')
    logger.info('Starting client')

    reader, writer = await asyncio.open_connection(server, port)

    while True:

        data = await reader.read(10000)

        await process_data(data)


        logger.info(f'Received: {data.decode()!r}')

        message = 'hi'
        logger.info(f'Send: {message!r}')
        writer.write(message.encode())
        await writer.drain()

        #writer.close()
        #await writer.wait_closed()

async def process_data(data):
    """
    Process the data sent by the server
    """
    # convert to dict
    data = json.loads(data)
    stdscr.addstr(10, 10, data)
    stdscr.addstr(0, 0, "HI THERE")
    stdscr.refresh()



# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Client for humans of th Hacker Grid World Server. Version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Amount of verbosity. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Amount of debugging. This shows inner information about the flows.', action='store', required=False, type=int)

    args = parser.parse_args()
    #logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s',)
    #logging.info('Client started')


    try:
        #logging.debug('Clientstart')
        asyncio.run(client('127.0.0.1', 9000))
    except Exception as e:
        pass
        #logging.error(f'Error: {e}')
    finally:
        #curses.endwin()
        #logging.debug('Goodbye')
        pass