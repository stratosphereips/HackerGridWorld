# Hacker Grid World
A client-server game to train and play with remote reinforcement learning in a Hacker Grid World.

# Use

    git clone https://github.com/stratosphereips/HackerGridWorld.git
    cd HackerGridWorld
    conda env create -f conda-environment.yml
    conda activate HGW
    # Start server and client in different consoles, or use tmux
    tmux new-session -d -s HGW-server 'python server.py -c HGW.server.conf'
    python ./client.py



# The list of emojis can be consulted here
~/miniconda3/envs/HGW/lib/python3.9/site-packages/pip/_vendor/rich/_emoji_codes.py

https://unicode.org/emoji/charts/emoji-list.html