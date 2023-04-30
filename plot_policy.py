#!/usr/bin/env python
# Policy plotter for the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023
import os
import argparse
import logging
import numpy as np
import json

__version__ = 'v0.1'



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Hacker Grid World Policy Plot version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Verbosity level. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Debugging level. This shows inner information about the flows.', action='store', required=False, type=int)
    parser.add_argument('-f', '--policyfile', help='Policy file.', action='store', required=True, type=str)
    parser.add_argument('-c', '--configfile', help='The server\' config file.', action='store', required=True, type=str)

    args = parser.parse_args()
    logging.basicConfig(filename='policy_plot.log', filemode='a', format='%(asctime)s, %(name)s: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

    with open(args.configfile, 'r') as jfile:
        obj_icons = {}
        confjson = json.load(jfile)
        w_size = confjson['world']['size_x']
        for obj in confjson['objects']:
            if obj == 'output_gate':
                gate_x = confjson['objects'][obj]['x']
                gate_y = confjson['objects'][obj]['y']
                gate_pos = gate_x + (gate_y * w_size)
                gate_icon = '🚪'
                obj_icons[gate_pos] = gate_icon
            elif 'goal' in obj:
                goal_x = confjson['objects'][obj]['x']
                goal_y = confjson['objects'][obj]['y']
                goal_pos = goal_x + (goal_y * w_size)
                goal_icon = '💰'
                obj_icons[goal_pos] = goal_icon

    actions={0:'⬆️', 1:'⬇️', 2:'⬅️', 3:'➡️'}
    q_table = np.load(args.policyfile)
    row = []
    for i in range(len(q_table)):
    # From the end to the start
        q_values = [q_table[i][0], q_table[i][1], q_table[i][2], q_table[i][3]]
        action_val_choosen = np.argmax(q_values)
        action_choosen = actions[action_val_choosen]
        if args.verbose:
            print(f'Line {i}: Action: {action_choosen}. Qvalues: {q_values}')
        object_icon = '⬛️'
        for obj in obj_icons:
            #print(obj, i)
            if i == int(obj):
                #print(f'Adding obj {obj}{obj_icons[obj]} to position {i}')
                object_icon = obj_icons[obj]
        #print(f'Position {i}. Adding action {action_choosen} and icon {object_icon}')
        row.append(action_choosen + ' ' + object_icon)
        if len(row)%10 == 0:
            print(row)
            row = []