# Software Set Up (THIS IS CURRENTLY A DRAFT)
This documentation includes the relevant information on how to set up the software frome scratch.

The following software has been tested on Raspberry Pi OS ....


## Raspberry Pi OS
The Raspberry Pi OS can be installed on a usb stick or SD card by using the Raspberry Pi Imager as described [here](https://www.raspberrypi.com/software/).

We recomend using Raspberry Pi OS .... as it the most recent version we have tested on.


## Visual Studio Code
To install VS Code on Raspberry Pi run the following
```
sudo apt update
sudo apt install code
```
For more information visit [here](https://code.visualstudio.com/docs/setup/raspberry-pi)


## git for collaborators
This section is for collaborators when setting up a new Raspberry Pi.

First the users name and email needs to be add this can be done by editing and running the following.
```
  git config --global user.email "you@example.com"
```
```
  git config --global user.name "Your Name"
```



## Users
If you are looking to use our software, run the following 
```
  git clone https://github.com/QUB-ASL/bzzz.git
```
