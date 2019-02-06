export FLASK_APP=src/index.py

init:
	flask initdb
run:
	flask run
