# Software Set Up (THIS IS CURRENTLY A DRAFT)
This documentation includes the relevant information on how to set up the software frome scratch.

The following software has been tested on Raspberry Pi OS ....


## Raspberry Pi OS
The Raspberry Pi OS can be installed on a usb stick or SD card by using the Raspberry Pi Imager as described [here](https://www.raspberrypi.com/software/).

We recomend using Raspberry Pi OS .... as it the most recent version we have tested on.


## Raspberry pi Configuration
To be able to access some of the GPIO pins properly the Pi must be configured.

- Run the following
```
sudo raspi-config
```
- Select **3 Interface options**
- Select **4 I2C**
- Select **Yes**

- Select **3 Interface options**
- Select **5 Serial port**
- Select **No**
- Select **Yes** 


## Visual Studio Code
To install VS Code on Raspberry Pi run the following
```
sudo apt update
sudo apt install code
```
For more information visit [here](https://code.visualstudio.com/docs/setup/raspberry-pi)


## git for collaborators
This section is for collaborators when setting up a new Raspberry Pi. Open a new terminal and carry out the following.

First the users name and email needs to be add this can be done by editing and running the following.
```
  git config --global user.email "you@example.com"
```
```
  git config --global user.name "Your Name"
```

Next an SSH key needs to be generated and added to the ssh-agent and GitHub account.

To generate an SSH key copy and paste the text below, substituting in your GitHub email address.

```
ssh-keygen -t ed25519 -C "your_email@example.com"
```
When prompted to "Enter a file in which to save the key", you can press Enter to accept the default file location.

When prompted to "Enter passpharse", type the same passpharse used for the other devices on this project for continuity.

When prompted to "Enter same passpharse again", Enter same the passpharse as before.

To add the SSH key to the ssh-agent run the following
```
ssh-add ~/.ssh/id_ed25519
```
for more information on Generating a new SSH key and adding it to the ssh-agent visit [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

To add the SSH key to your GitHub account follow the [guide line](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)

After all the above steps are complete run the following 
```
git clone git@github.com:QUB-ASL/bzzz.git
```


## Users
If you are looking to use our software, run the following 
```
  git clone https://github.com/QUB-ASL/bzzz.git
```
