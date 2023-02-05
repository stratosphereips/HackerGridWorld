#!/usr/bin/env python
# Server for the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023

import argparse
from datetime import datetime
import logging
import json

import asyncio

__version__ = 'v0.1'

async def server(host, port):
    """
    Start the socket server
    Define the function to deal with data
    """
    logger = logging.getLogger('SERVER')
    logger.info('Starting server')
    server = await asyncio.start_server(handle_new_client, host, port)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    logger.info(f'Serving on {addrs}')
    async with server:
        await server.serve_forever()

async def handle_new_client(reader, writer):
    """
    Function to deal with each new client
    """
    logger = logging.getLogger('SERVER')
    addr = writer.get_extra_info('peername')
    logger.info(f"Handling data from client {addr}")

    # Get a new world
    world = init_hgw()

    while True:
        answer = world
        # Convert world to json before sending
        world_json = json.dumps(world)
        print(f"Sending: {world_json!r}")
        writer.write(bytes(str(world_json).encode()))
        await writer.drain()

        # Every x seconds, send it again
        #await asyncio.sleep(1)
        #writer.write(bytes(str(world_json).encode()))

        data = await reader.read(10)
        message = data.decode()

        logger.info(f"Received {message!r} from {addr}")


def init_hgw():
    """
    Initialize the web server
    Returns a dictionary
    """
    world_conf = confjson.get('world', None)
    size_x = world_conf.get('size_x', None)
    size_y = world_conf.get('size_y', None)

    # Create the world as a list
    world = {}
    world["size"] = str(size_x) + 'x'+ str(size_y)
    world["score"] = 100
    positions = []
    for pos in range(size_x*size_y):
        positions.append('')
    positions[0] = 'ghost'
    world["positions"] = positions
    # Fill with some things

    return world


# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Hacker Grid World Server version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Amount of verbosity. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Amount of debugging. This shows inner information about the flows.', action='store', required=False, type=int)
    parser.add_argument('-c', '--configfile', help='Configuration file.', action='store', required=True, type=str)

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s',)

    with open(args.configfile, 'r') as jfile:
        confjson = json.load(jfile)

    try:
        logging.debug('Server start')
        asyncio.run(server(confjson.get('HOST', None), confjson.get('PORT', None)))
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        logging.debug('Goodbye')