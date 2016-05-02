EditOnline
===============
A simple online text file editor base on Ace.js.

Install
===============
::

 pip install EditOnline


Use
===============
cd to you working directory and run command:

::

 EditOnline

on Windows use:
::

 EditOnline.bat

if can't find EditOnline command, try:
::

 python -m EditOnline


open broswer with url **http://127.0.0.1:8000**
	

Editor shortcut
===============
- **Ctrl+S** : save file

- **Ctrl+Shif+N** : new file

- **Ctrl+H** : show help info

Other tips
===============
1.set http port 80
::

 EditOnline 80

2.authenticate with username and password (admin admin)
::

 EditOnline -u admin -p admin

3.set the working directory (/tmp)
::

 EditOnline -d /tmp

4.bind address with 127.0.0.1
::

 EditOnline 127.0.0.1:8000
 
5.use as wsgi
::

 # set username and passwor
 export WSGI_PARAMS="-u admin -p admin" 
 # run wsgi with gunicorn
 gunicorn -b 0.0.0.0:8000 EditOnline.wsgi:application