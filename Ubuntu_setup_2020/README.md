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
 * Github still asks for username when I push.  Maybe it takes time?
 
 1/13/21
 
 Wireless was not working.  Re-installed Ubuntu, and it still did not work.  Followed this suggestion:  From  https://askubuntu.com/questions/1305699/bcmwl-kernel-source-broken-on-kernel-5-8-0-34-generic

"The reason is obvious. Almost every time Canonical rolls out a HWE kernel, they forget to upgrade bcmwl-kernel-source in the repos.

You have two solutions (use one or the other, it makes no sense to use both):

    Install bcmwl-kernel-source from groovy repos. You can find it e.g. here. http://mirrors.kernel.org/ubuntu/pool/restricted/b/bcmwl/bcmwl-kernel-source_6.30.223.271+bdcom-0ubuntu7_amd64.deb It will compile with the 5.8 kernel.

Download the deb and install it by

sudo dpkg -i bcmwl-kernel-source_6.30.223.271+bdcom-0ubuntu7_amd64.deb.

This seems to work.

Now reinstall everything!
KiCad, Freecad, Chrome, magick, inkscape, gimp, 

1/20/21

Here is a good VIM tutorial! : https://www.linux.com/training-tutorials/vim-101-beginners-guide-vim/

1/223/21

Vim book here:  http://www.eandem.co.uk/mrw/vim/usr_doc/a4s_bm.pdf
Liking VIM.  Perfect language to learn during a pandemic.

1/26/21

Put bash aliases in .bash_aliases.  These get installed on startup.

