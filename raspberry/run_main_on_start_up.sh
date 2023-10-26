#!/bin/bash

source ~/venv_bzzz/bin/activate
cd ~/bzzz/raspberry
sudo pigpiod
python main.py