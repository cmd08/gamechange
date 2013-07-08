gamechange
==========

Welcome to the Gamechange developers repository - to get yourself setup simply follow these instructions below:

1) Install and setup the virtual environment. In a terminal type:
	a) sudo apt-get install python-virtualenv

	b) mkdir ~/python

	c) cd ~/python

	d) virtualenv gamechange

2) Obtain the correct repository for developers. In the same terminal type:
	a) cd gamechange

	b) git init

	c) git remote add origin git@github.com:YOURGITUSERNAMEHERE/gamechange.git

	d) git pull origin master

	e) git remote add king git@github.com:cmd08/gamechange.git

	f) git remote set-url --push king DONT_DO_THAT!

3) Setup dependencies. In the same terminal type:
	a) cp conf.default conf

	b) export FLASK_CONFIG=/home/YOUUSERNAMEHERE/python/gamechange/conf

	c) source bin/activate

	d) pip install -r "pip.txt"

4) Setup the database. In the same terminal type:
	a) sudo apt-get install mysql-server

	b) FML FML FML FML FML

5) GET DEVELOPING!!