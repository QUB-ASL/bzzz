<p align="center">
<img width="300" alt="bzzz-logo" src="design/logo/bzzz-logo.png">
</p>

<p align="center">
<em>Programmable quadcopter with ESP32 and RaspberryPi</em>
</p>


## Project Description

The autonomous systems lab at the school of EEECS of Queens Univeristy Belfast (QUB) has designed and built a quadcopter with a stabilising attitude control system and (as of v0.2.0) altitude hold. This is part of an ongoing research project whose objective is the development of control methodologies that will enable quadcopters to fly in extreme weather conditions. Currently, the quadcopter can be operated using a radio controller (RC).


## Getting started

- [Safety first](SAFETY.md): read the safety guidelines
- [Contributing to this project](CONTRIBUTING.md)
- [PCB design](design/README.md)
- [ESP32 documentation](include/README.md), [headers](./include) and [sources](./src)
- [Raspberry Pi code](raspberry/README.md)
- [Create a Discord bot](raspberry/DiscordBot/README.md)


## How to Fly 
*This is the current set up for how to fly the quadcopter. In the future the user will not have to SSH into the Pi*

- Make sure the quadcopter is in a safe place to fly
- Power on the battery
- SSH into the Raspberry Pi
- Make sure the Pi is on the correct branch and the ESP32 is uploaded with correct code
- Activate the virtual environment located on the `Desktop` by
```
source ../venv/bin/activate
```
- Run the main python script by 
```
python raspberry/main.py
```
- Turn on the remote and wait to connect
- Arm the quadcopter by switch B
- Fly safely
- Switch D kills the quadcopter


## Videos 

<p>Testing altitude hold of bzzz:</p>

[![Watch the video](https://img.youtube.com/vi/AMWUkB0SQi4/hqdefault.jpg)](https://youtu.be/AMWUkB0SQi4)

<p>First flight of bzzz:</p>

[![Watch the video](https://img.youtube.com/vi/eGNW_-LX130/hqdefault.jpg)](https://youtu.be/eGNW_-LX130)

<p>Preliminary tests in the lab:</p>

[![Watch the video](https://img.youtube.com/vi/7mFDusj9uvs/hqdefault.jpg)](https://youtu.be/7mFDusj9uvs)
