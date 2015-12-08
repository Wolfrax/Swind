#!/bin/bash
# See https://help.github.com/articles/generating-ssh-keys/ to enable SSH to GitHub, needed for script
echo ---------------------
date
cd /home/pi/app/Swind
echo Update Swind
git pull
python py/getSMHI.py
git add data            # Add all new files in data-folder
git rm -f data/OLD_*.js # Remove all files marked with "OLD_"-prefix by getSMHI.py
git commit -a -m 'Latest day'
git push origin master
echo Update Wolfrax web
cd ../wolfrax.github.io
git pull
git rm -f Swind/data/*.js
cp -p ../Swind/data/*.js Swind/data
git add Swind/data/
git commit -a -m 'Latest day'
git push origin master
echo =====================
echo