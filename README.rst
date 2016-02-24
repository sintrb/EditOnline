# EditOnline

A simple online file editor by Python base on Ace.js.

## How To Use

0. cd to you working dir

1. run command: python -m EditOnline

2. use broswer open 'http://127.0.0.1:8000'
	
in broswer editor:

- Ctrl+S : save file

- Ctrl+Shif+N : new file

- Ctrl+H : show help info

## Other

- set http port 80: python -m EditOnline 80

- authenticate with username and password (admin admin): python -m EditOnline -u admin -p admin

- set the working directory (/tmp): python -m EditOnline -d /tmp
