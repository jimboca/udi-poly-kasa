#!/usr/bin/env bash

#echo ""
#if [ -e python-kasa ]; then
#  echo "Updating python-kasa..."
#  cd python-kasa
#  git pull
#  cd ..
#else
#  git clone https://github.com/jimboca/python-kasa.git
#fi

repo=pyHS100
if [ -e $repo ]; then
  echo "Updating $repo ..."
  cd $repo
  git pull
  cd ..
else
  git clone https://github.com/jimboca/$repo
fi

if [  $# -gt 0 ]; then
  echo "Skipping pip3 install, must be a travis run?"
else
  sudo pip install --upgrade pip
  pip3 install -r requirements.txt --user --no-warn-script-location
fi
