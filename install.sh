#!/usr/bin/env bash

if [  $# -gt 0 ]; then
  echo "Skipping pip3 install, must be a travis run?"
else
  pip3 install -r requirements.txt --user
fi
