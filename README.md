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

	b) source bin/activate

	c) pip install -r "pip.txt"

	d) deactivate

	e) sudo apt-get install virtualenvwrapper

	f) git clone git://github.com/kennethreitz/autoenv.git ~/.autoenv

	g) echo 'source ~/.autoenv/activate.sh' >> ~/.bashrc

	h) Now make a file called gamechange.env in the ~/python/gamechange directory and add the following to the file:

		source /home/YOURUSERNAMEHERE/python/gamechange/bin/activate
		export FLASK_CONFIG=/home/YOURUSERNAMEHERE/python/gamechange/conf

	i) restart the terminal

	j) Test the setup now by typing cd ~/python/gamechange and you should see (gamechange) at the start of the new line

	k) git submodule init

	l) git submodule update

	m) cd healthgraph-api

	n) python setup.py install

4) Test the basics. In the same terminal type:

	a) ./runserver.py

	b) Take the web address given and open this in your favourite web browser. You may find some problems with the display of the page. If this is the case then simply replace the ip address with localhost e.g. http://localhost:8001/

5) Setup the database. In the same terminal type:
	
	a) sudo apt-get install mysql-server

	b) FML FML FML FML FML

6) GET DEVELOPING!!