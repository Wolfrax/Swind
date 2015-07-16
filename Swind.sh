#!/bin/bash
# See https://help.github.com/articles/generating-ssh-keys/ to enable SSH to GitHub, needed for sript
echo ---------------------
date
cd /var/www/Swind
python /var/www/Swind/py/getSMHI.py
git pull
git add ./data
git commit -q -m 'Latest day'
git push -q origin master
