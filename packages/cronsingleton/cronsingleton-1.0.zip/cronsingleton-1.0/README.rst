=============
cronsingleton
=============

A user level forground running process which accepts a cron spec and command which will be executed accordingly. Be sure to wrap the cron spec in single quotes to prevent shell globbing.

  $ cronsingleton '* * * * *' notifiy-send "hello"

If you specifiy a file as a signle argument to cronsingleton then that file is parsed as a cron script.

  $ cronsingleton mycronfile.conf

