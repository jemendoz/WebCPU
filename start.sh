#!/bin/bash

if [ ! -d ".venv" ]; then
  echo Making virtual environment...
  python3 -m venv .venv
  source .venv/bin/activate
  echo Installing dependencies...
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

reflex run

