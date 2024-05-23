#!/usr/bin/env bash

if [ ! -d "pong_cli/env" ]; then
	python3 -m venv pong_cli/env
	source pong_cli/env/bin/activate
	pip install -r requirements.txt
	python3 pong_cli/pong_cli.py
	deactivate
else
	echo "Already built"
fi

# To activate, run the following line in /pong_cli
# source env/bin/activate