# Workflow for Swind

This describes the intended workflow for Swind project
It is based on the following nodes

* MacBook Air: The development node
* [Raspberry Pi](http://192.168.1.50/Swind/): Data collection server and local web-server for 
[Swind](http://192.168.1.50/Swind/) and [Wolfrax website](http://192.168.1.50/Wolfrax/)
* [Github](https://github.com/): Public [Wolfrax GitHub](https://github.com/Wolfrax/) repository and public 
[Wolfrax website](http://http://wolfrax.github.io/)

The idea is that development is made on the MacBook Air which push updates to GitHub. 

The Raspberry have dual purposes, as a local web server and as a data collector of SMHI data once per day.
As data is collected on the Raspberry, it will need as well to push this data to GitHub, bith to the Swind repository
and the public website. This is done in conjunction with the data collection, ie once per day.

**Important!** As data should not be duplicated, the Wolfrax site at the Raspberry have a directory that is symlinked
`/var/www/Wolfrax/data --> /var/www/Swind/data`. On GitHub, the data is however duplicated.

## MacBook Air
Used for development of software only. PyCharm IDE is used and the projects is available here:

* Swind - [/Users/mm/Dev/Swind](/Users/mm/Dev/Swind)
* Wolfrax - [/Users/mm/Dev/wolfrax.github.io](/Users/mm/Dev/wolfrax.github.io)

When files are changed they can be 

1. **Pushed** to GitHub through `VCS->Git->Push...`
2. **Deployed** to the Raspberry Pi environment through `Tools->Deployment->Upload to 192.168.150`

Option 1 is **preferred** for both projects

## Raspberry Pi (192.168.1.50)
Used as a local data collection server (`getSMHI.py`) and web-server.

`Swind` (data collection) and `Wolfrax` (web-server) is located at `/var/www`, accessible as
[http://192.168.1.50/Swind/](http://192.168.1.50/Swind/) and 
[http://192.168.1.50/Wolfrax](http://192.168.1.50/Wolfrax) respectively.

`getSMHI.py` is located at `/var/www/Swind/py/` and is used through the script `Swind.sh` located at `/var/www/Swind/`
`Swind.sh` is executed daily through `crontab`

        # m h dom mon dow user  command
       00 8    * * *   pi      sh /var/www/Swind/Swind.sh >> /var/log/Swind.log 2>&1

The output is logged to `/var/log/Swind.log` and a symlink is available at `/var/www/Swind/Swind.log`

Through the script `getSMHI.py` is invoked once per day and a new file (such as `2015-07-16.js`) is created in
`/var/www/Swind/data`. This file is then copied to `/var/www/Swind/Swind.js` which always contain the latest data.
Files older than 7 days are copied to `/var/www/Swind/data/old` which is not included in the Git repository.

Once the script have executed a `git pull` command is issued, this will update the repository from GitHub if needed.
Then `git add ./data` is executed to add the newly generated files, following this `git commit -q -m 'Latest day'` and
`git push -q origin master`. This will push the latest generated files to the GitHub repository Swind.

If method 1) ( **Pushed** ) **and** method 2) in MacBook Air ( **Deployed** ) is used git will complain that there 
is a collision. 

Hence, files should be **pushed** from MacBook Air to GitHub, then **pulled** by Raspberry Pi from GitHub.

## Markdown
This documentation is written using Markdown.

[Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

Python script converting Markdown to HTML `sudo easy_install markdown`.

Command line usage `python -m markdown workflow.md -f workflow.html`
