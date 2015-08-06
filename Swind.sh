#!/bin/bash
# See https://help.github.com/articles/generating-ssh-keys/ to enable SSH to GitHub, needed for script
echo ---------------------
date
echo Update Swind
cd /var/www/Swind
python /var/www/Swind/py/getSMHI.py
git pull
git add data            # Add all new files in data-folder
git rm -f data/OLD_*.js # Remove all files marked with "OLD_"-prefix by getSMHI.py
git commit -a -m 'Latest day'
git push origin master
echo Update Wolfrax web
cd /var/www/Wolfrax
git pull
git rm -f /var/www/Wolfrax/Swind/data/*.js
cp -p /var/www/Swind/data/*.js /var/www/Wolfrax/Swind/data
git add Swind/data/
git commit -a -m 'Latest day'
git push origin master
echo =====================
echo