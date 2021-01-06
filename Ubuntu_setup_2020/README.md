## Setup old Dell computer with Ubuntu 20.04.1 

to get version, (in command line, "lsb_release -a")

### Jupyter Notebook for python.

follow directions to install Jupyter notebook in virtual environment: [here](https://www.digitalocean.com/community/tutorials/how-to-set-up-jupyter-notebook-with-python-3-on-ubuntu-18-04).

To get to virtual environment, type "source ~/Jupyter/Jupyter_env/bin/activate".  Then, once in the environment, type "jupyter notebook".


## Set up MacBook Pro (mid 2012) with 20.04.

12/25/20.  12/26/20 

 * Follow instructions [here](https://ubuntu.com/tutorials/create-a-usb-stick-on-macos#1-overview) to create bootable usb on Mac.
 * Got wireless working by choosing network at start and/or checking box to install proprietary drivers during installation dialog.
 * update, then upgrade.  Probably want 'apt-get dist-upgrade'
 * Neil's installation scripts [here](http://academy.cba.mit.edu/classes/project_management/scripts/Ubuntu_20.04)
 
 1/6/21
 
 * Generate an ssh key on the laptop, using 'ssh-keygen -t rsa'.  The public key will be stored in Github.  The private key stays in ~/.ssh/id_rsa
 * 
