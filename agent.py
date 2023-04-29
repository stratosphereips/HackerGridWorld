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
import pickle


__version__ = 'v0.2'

class q_learning(object):
    """
    Learning models should have this API

    act(world): To receive a Game() object

    """
    def __init__(self, theworld):
        self.q_table = []
        #self.actions = {'0':'KEY_UP', '1':'KEY_DOWN', '2':'KEY_LEFT', '3':'KEY_RIGHT'}
        self.actions = ['KEY_UP', 'KEY_DOWN', 'KEY_LEFT', 'KEY_RIGHT']
        self.last_action = -1
        self.learning_rate = confjson.get('learning_rate', 0.1)
        self.epsilon_start = confjson.get('epsilon_start', 1)
        self.epsilon_end = confjson.get('epsilon_end', 0)
        self.max_episodes_epsilon = confjson.get('epsilon_max_episodes', 3000)
        self.epsilon = self.epsilon_start
        self.gamma = confjson.get('gamma', 0.9)
        self.n_episodes_evaluate = confjson.get('n_episodes_evaluate', 100)
        self.world = {}
        self.world['size_x'] = theworld.size_x
        self.world['size_y'] = theworld.size_y
        self.current_state = theworld.current_state
        self.prev_state = self.current_state
        self.score = 0
        self.best_score = float('-inf')
        self.last_episode_scores = []
        self.reward = theworld.current_reward
        self.logger = logging.getLogger('AGENT')
        self.episodes = 0
        self.end = theworld.end

        # Where to save the models
        self.behavioral_model_filename = 'behavioral-model'
        self.target_model_filename = 'target-model'

        # If repaly mode, load the model
        if args.replayfile:
            # Load
            self.q_table = np.load(args.replayfile)
            # Force no random
            self.epsilon_start = 0
            self.epsilon_end = 0
            self.epsilon = 0
        else:
            self.initialize_q_table(self.world)


    def initialize_q_table(self, world):
        """
        Init the q table values
        """
        # The q_table is a two dimensional vector of X positions of states, and each state has a vector of 4 actions
        # The X positions are in a continous vector
        self.q_table = np.zeros((self.world['size_x'] * self.world['size_y'], len(self.actions)))
        # Initialize with random?
        #self.q_table = np.random.rand(self.world['size_x'] * self.world['size_y'], len(self.actions))

    def update_world(self, theworld):
        """
        Update world
        """
        #self.logger.info(f'In update. Current_state: {self.current_state}')
        #self.logger.info(f'In update. The world current_state: {theworld.current_state}')
        # Store prev state
        self.prev_state = self.current_state
        self.current_state = theworld.current_state
        #self.logger.info(f'In update. now prev: {self.prev_state}. Now current {self.current_state}')
        self.reward = theworld.current_reward
        self.score += theworld.current_reward
        self.end = theworld.end

    def act(self, world):
        """
        Receive a world
        Return an action

        When the episode finishes, we automatically receive the new world, so 
        new states are ready.
        """
        # First select an action from the exploratory policy
        action = self.choose_action()
        return action

    def choose_action(self):
        """
        Choose an action following a policy
        """
        try:
            #self.logger.info('Choose action.')
            die = random.random()
            decay_rate = np.max( [(self.max_episodes_epsilon - self.episodes) / self.max_episodes_epsilon, 0])
            self.epsilon = (self.epsilon_start - self.epsilon_end ) * decay_rate + self.epsilon_end
            if die <= self.epsilon:
                # Random action e-greedy
                self.logger.info('Choosing random action.')
                action = random.randint(0, len(self.actions) - 1)
            else:
                # Choose the action that maximizes the value of this state
                values_actions = self.q_table[self.current_state]
                max_value = np.max(values_actions)
                # See if the max value appeared many times, and if yes break ties by choosing randomly between those indexes
                temp_values_actions = np.array(values_actions)
                indexes = np.where(temp_values_actions == max_value)[0]
                action = random.choice(indexes)
                self.logger.info(f'Choosing policy action. Action: {self.actions[action]}. Value: {max_value} from {values_actions}')
            
            # Store last action
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
        # Update world
        self.update_world(world)

        # If we are replaying, don't learn
        if not args.replayfile:
            try:
                # To get the value of Q(s', a')
                # Select the action that maximices the current policy
                values_actions = self.q_table[self.current_state]
                max_value = np.max(values_actions)
                # See if the max value appeared many times, and if yes break ties by choosing randomly between those indexes
                temp_values_actions = np.array(values_actions)
                indexes = np.where(temp_values_actions == max_value)[0]
                state_action_idx_max_value = random.choice(indexes)

                # Update Q(s, a)
                self.logger.info(f'Prev state: {self.prev_state}. Step Reward: {self.reward}. Next state: {self.current_state}. Next StateMaxValue: {self.q_table[self.current_state][state_action_idx_max_value]}. Idx: {state_action_idx_max_value}')
                self.logger.info(f'\tBefore update. Action Values: {self.q_table[self.prev_state]}.')
                self.q_table[self.prev_state][self.last_action] = self.q_table[self.prev_state][self.last_action] + (
                                                self.learning_rate * (
                                                    self.reward + 
                                                    (self.gamma * self.q_table[self.current_state][state_action_idx_max_value]) - 
                                                    self.q_table[self.prev_state][self.last_action] 
                                                    ) 
                                                )
                self.logger.info(f'\tAfter  update. Action Values: {self.q_table[self.prev_state]}.')
            except Exception as e:
                self.logger.error(f'Error in learn: {e}')

    def game_ended(self):
        """
        End of episode
        """
        # Score we got in the last game
        self.last_episode_scores.append(self.score)
        #self.logger.error(f'Episode score: {self.score}')
        self.episodes += 1

        if not args.replayfile:
            # Store best model
            if self.score > self.best_score:
                self.logger.critical(f'Saving model of behavioral policy due to best score ever. After {self.episodes} episodes, score: {self.score}. Files "{self.behavioral_model_filename}*"')
                # Save txt
                with open(self.behavioral_model_filename + '.txt', 'w+') as fi:
                    fi.write(str(self.q_table))
                # Save npy
                np.save(self.behavioral_model_filename, self.q_table)
                self.best_score = self.score

            if self.episodes % self.n_episodes_evaluate == 0:
                avg_scores = np.average(self.last_episode_scores)
                self.logger.critical(f'Episodes elapsed: {self.episodes}. Avg Scores in last 100 episodes: {avg_scores:.4f}. Epsilon: {self.epsilon:.5f}. Saving target policy in files "{self.target_model_filename}*"')
                # Save txt
                with open(self.target_model_filename + '.txt', 'w+') as fi:
                    fi.write(str(self.q_table))
                # Save npy
                np.save(self.target_model_filename, self.q_table)

            self.logger.info('Episode of Agent ended.')
        # Reset the score to 0
        self.score = 0


class Game(object):
    """
    Game object
    """
    def __init__(self):
        self.size_x = 0
        self.size_y = 0
        self.world_score = 0
        #self.reward = 0
        self.world_positions = {}
        self.end = False
        self.current_state = -1
        self.current_reward = 0

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

            # Get key from agent, the action
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

            # With this new data, now learn
            agent_model.learn(myworld)

    except Exception as e:
        logging.error(f'Error in start_agent: {e}')


def check_end(myworld):
    """
    Check if we reached the end
    """
    if myworld.end:
        # Game end
        logging.info(f'Game ended: Score: {myworld.world_score}')
        myworld.world_score = 0
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
        myworld.current_reward = data['reward']
        myworld.world_score += myworld.current_reward
        myworld.world_positions = data['positions']
        myworld.current_state = data['current_character_position']
        myworld.end = data['end']
        # Print positions
        minimum_y = 10
        # In the console graph Y grows going down and X grows to the right
        for x in range(myworld.size_x):
            for y in range(myworld.size_y):
                w.addstr(y + minimum_y, x, emoji.emojize(str(myworld.world_positions[x + (y * 10)])))
        # Print score
        w.addstr(minimum_y + myworld.size_y + 1, 0, f"Reward: {str(myworld.current_reward):>5}") 
        w.addstr(minimum_y + myworld.size_y + 2, 0, f"Score: {str(myworld.world_score):>5}") 

      
    except Exception as e:
        logging.error(f'Error in process_data: {e}')

def print_action(action, myworld, w):
    """
    Print the action from the agent
    """
    minimum_y = 10
    w.addstr(myworld.size_y + minimum_y + 3, 0, f'{action:<15}')
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
    
    # Start the agent
    start_agent(w, sock)

    sock.close()

# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Client for humans of th Hacker Grid World Server. Version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Amount of verbosity. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Amount of debugging. This shows inner information about the flows. INFO, DEBUG, ERROR, CRITICAL', action='store', required=False, type=str)
    parser.add_argument('-s', '--server', help='IP of game server.', action='store', required=False, type=str, default='127.0.0.1')
    parser.add_argument('-p', '--port', help='Port of game server.', action='store', required=False, type=int, default=9000)
    parser.add_argument('-c', '--configfile', help='Configuration file.', action='store', required=True, type=str)
    parser.add_argument('-r', '--replayfile', help='Used this saved model strategy to play in human time.', action='store', required=False, type=str)

    args = parser.parse_args()
    logging.basicConfig(filename='agent.log', filemode='a', format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',level=logging.INFO)

    with open(args.configfile, 'r') as jfile:
        confjson = json.load(jfile)

    try:
        curses.wrapper(main)
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        logging.debug('Goodbye')