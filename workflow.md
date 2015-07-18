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
As data is collected on the Raspberry, it will need as well to push this data to GitHub, both to the Swind repository
and the public website. This is done in conjunction with the data collection, ie once per day.

## MacBook Air
Used for development of software only. PyCharm IDE is used and the projects is available here:

* Swind - [/Users/mm/Dev/Swind](/Users/mm/Dev/Swind)
* Wolfrax - [/Users/mm/Dev/wolfrax.github.io](/Users/mm/Dev/wolfrax.github.io)

When files are changed they can be pushed to GitHub through `VCS->Git->Push...`

## Raspberry Pi (192.168.1.50)
Used as a local data collection server and web-server.

`Swind` (data collection) and `Wolfrax` (web-server) is located at `/var/www`, accessible as
[http://192.168.1.50/Swind/](http://192.168.1.50/Swind/) and 
[http://192.168.1.50/Wolfrax](http://192.168.1.50/Wolfrax) respectively.

`getSMHI.py` is located at `/var/www/Swind/py/` and is used through the script `Swind.sh` located at `/var/www/Swind/`
`Swind.sh` is executed daily through `crontab`

       00 8    * * *   pi      sh /var/www/Swind/Swind.sh >> /var/log/Swind.log 2>&1

Remember `sudo chmod g+x -R getSMHI.py`
I changed the ownership of the /var/www/ directory from root to Pi through `sudo chown -R pi /var/www/`.

If the system time (use `date` at the Raspberry command prompt) is configured to the wrong timezone, us the following 
command `sudo dpkg-reconfigure tzdata` to correct.

To enable git push to GitHub repository, SSH needs to be configured.
Refer to these GitHub pages:

1. [Generating SSH keys] (https://help.github.com/articles/generating-ssh-keys/)
2. [Changing a remote URL] (https://help.github.com/articles/changing-a-remote-s-url/)

The output is logged to `/var/log/Swind.log` and a symlink is available at `/var/www/Swind.log`

Through the script `getSMHI.py` is invoked once per day and a new file (such as `2015-07-16.js`) is created in
`/var/www/Swind/data`. This file is then copied to `/var/www/Swind/Swind.js` which always contain the latest data.
Files older than 7 days are copied to `/var/www/Swind/data/old` which is not included in the Git repository.

Once the script have executed a `git pull` command is issued, this will update the repository from GitHub if needed.
Then `git add ./data` is executed to add the newly generated files, following this `git commit -q -m 'Latest day'` and
`git push -q origin master`. This will push the latest generated files to the GitHub repository Swind.

## Markdown
This documentation is written using Markdown.

[Cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

Python script converting Markdown to HTML `sudo easy_install markdown`.

Command line usage `python -m markdown workflow.md -f workflow.html`
