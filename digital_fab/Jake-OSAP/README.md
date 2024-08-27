sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y build-essential libssl-dev zlib1g-dev libncurses5-dev \
libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev \
libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev libnss3-dev wget


cd /tmp
wget https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz



tar -xf Python-3.12.2.tgz
cd Python-3.12.2


./configure --enable-optimizations


make -j 4
sudo make altinstall
