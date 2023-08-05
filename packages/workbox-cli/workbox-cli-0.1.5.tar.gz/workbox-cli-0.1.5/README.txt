======================
Confluence WorkBox CLI
======================

The Confluence WorkBox CLI allows you to work with your WorkBox tasks
via the command line.

Configuration
=============

To use workbox, you'll need to create a .workbox configuration file in your
home directory. In this configuration file you can specify as many Confluence
servers as you would like, each requiring a base URL, username and password.

An example configuration file::

    [MyConf]
    base_url = "https://foo.com/wiki"
    username = "xxx"
    password = "yyy"

Commands
========

Available commands for WorkBox CLI::

    $ workbox list #list your tasks
    $ workbox add "Task 1" "Task 2" #add tasks
    $ workbox complete 2 #complete a task
    $ workbox rm 2 #remove a task

Support
=======

To raise a bug, please visit http://bitbucket.org/samtardif/workbox-cli
