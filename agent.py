#!/usr/bin/env python
# Agent to automatically play the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023

import argparse
from datetime import datetime
import logging
import json
import curses
import socket
import time
import emoji
import numpy as np
import random


__version__ = 'v0.1'

class q_learning(object):
    """
    Learning models should have this API

    act(world): To receive a Game() object

    """
    def __init__(self, theworld):
        self.q_table = []
        self.actions = {'0':'KEY_UP', '1':'KEY_DOWN', '2':'KEY_LEFT', '3':'KEY_RIGHT'}
        self.step_seze = 0.01
        self.epsilon = 0.001
        self.world = {}
        self.world['size_x'] = theworld.size_x
        self.world['size_y'] = theworld.size_y
        self.score = theworld.world_score
        self.end = theworld.end
        self.initialize_q_table(self.world)

    def initialize_q_table(self, world):
        """
        Init the q table values
        """
        """
        for x in self.world['size_x']:
            for y in self.world['size_y']:
                state = []
                for action in self.actions.keys():
                    state.append = 0
                self.q_table.append(state)
        """
        np.zeros((self.world['size_x'], self.world['size_y'], len(self.actions)))

    def act(self, world):
        """
        Receive a world
        Return an action

        When the episode finishes, we automatically receive the new world, so 
        new states are ready.
        """
        # Update world
        self.update_world(world)

        # First select an action from the exploratory policy
        action = self.choose_action()
        return action

    def choose_action(self):
        """
        Choose an action following a policy
        """
        try:
            #self.logger.info('Choose action.')

            # Store prev state
            self.prev_state = self.current_state

            actions_state = self.q_table[self.current_state]
            die = random.random()
            if die <= self.epsilon:
                # Random action e-greedy
                #self.logger.info('Choosing random greedy.')
                action = random.randint(0, len(self.actions) - 1)
            else:
                #self.logger.info('Choosing max.')
                # Choose the action that maximizes the value of this state
                values_actions = self.q_table[self.current_state]
                action = np.argmax(values_actions)
            
            # Store last action
            self.logger.info(f'Updating last action {self.last_action} with {action}')
            self.last_action = action
            
            action_name = self.actions[action]
            return action_name
        except Exception as e:
            self.logger.error(f'Error in choose_action: {e}')

    def learn(self, world):
        """
        Update the target policy to learn from the
        last step
        """
        try:
            state_max_value = np.argmax(self.q_table[self.current_state])
            self.q_table[self.prev_state][self.last_action] = self.q_table[self.prev_state][self.last_action] + self.step_size * (self.reward + (self.gamma * state_max_value) - self.q_table[self.prev_state][self.last_action] ) 
            self.logger.info(f'Prev state: {self.prev_state}, Action Values: {self.q_table[self.prev_state]}')
        except Exception as e:
            self.logger.error(f'Error in learn: {e}')

    def game_ended(self):
        """
        End of episode
        """
        logger = logging.getLogger('AGENT')
        logger.info('Episode of Agent ended.')



class Game(object):
    """
    Game object
    """
    def __init__(self):
        self.size_x = 0
        self.size_y = 0
        self.world_score = 0
        self.world_positions = {}
        self.end = False

def start_agent(w, sock):
    """
    Start the socket server
    Define the function to deal with data
    """
    try:

        logger = logging.getLogger('AGENT')
        logger.info('Starting agent')

        myworld = Game()

        # Get data from server
        net_data = sock.recv(2048)
        logger.info(f'Received: {net_data.decode()!r}')

        # Process data, print world
        process_data(myworld, net_data, w)

        # Here we load the model we want
        agent_model = q_learning(myworld)

        while True:
            # Check end
            if check_end(myworld):
                # The game ended
                agent_model.game_ended()
                # Get the new map to reset
                net_data = sock.recv(2048)
                logger.info(f'Received: {net_data.decode()!r}')
                # Process data, print world
                # The world is resseted by the server, here we just load it
                process_data(myworld, net_data, w)

            # Get key from agent
            key = agent_model.act(myworld)

            # Print the action
            print_action(key, myworld, w)

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

            # Get data from server
            net_data = sock.recv(2048)
            logger.info(f'Received: {net_data.decode()!r}')

            # Process data, print world
            process_data(myworld, net_data, w)


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

def print_action(action, myworld, w):
    """
    Print the action from the agent
    """
    minimum_y = 10
    w.addstr(myworld.size_y + minimum_y + 2, 0, f'{action:<15}')
    w.refresh()


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
    start_agent(w, sock)

    sock.close()

# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Client for humans of th Hacker Grid World Server. Version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Amount of verbosity. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Amount of debugging. This shows inner information about the flows.', action='store', required=False, type=int)
    parser.add_argument('-s', '--server', help='IP of game server.', action='store', required=False, type=str, default='127.0.0.1')
    parser.add_argument('-p', '--port', help='Port of game server.', action='store', required=False, type=int, default=9000)

    args = parser.parse_args()
    logging.basicConfig(filename='agent.log', filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',level=logging.INFO)


    try:
        curses.wrapper(main)
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        logging.debug('Goodbye')