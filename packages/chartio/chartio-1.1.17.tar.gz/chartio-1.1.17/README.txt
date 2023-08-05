=======
Chartio
=======

Chartio utilities for providing read-only user local database access.

Version 1.1.17


Introduction
------------
This project permits Chartio customers to provide database access by
opening an SSH reverse tunnel from a Chartio server to the customer
database.

Errors, comments, questions may be sent to support at chart dot io.


Requirements
------------
Requires a read-only database role (or authorization to create one)
and a local SSH client.


Supported Databases
-------------------
MySQL
Oracle (command-line only)
PostgreSQL


Installation
------------
To install, type::

    $ python setup.py install

To uninstall, remove the files
    chartio_setup
    chartio_connect


Oracle
------
Connecting an Oracle datasource to Chartio requires an existing
Chartio login and a read-only database role. In addition, all
information must be specified on the chartio_setup command-line. For
example, to connect the Oracle database named 'sales' using the
existing read-only role of 'sales_user'

% chartio_setup --oracle --database-name=sales --role=sales_user

The script will the prompt you for your Chartio login and password
and for the password of the 'sales_user' role.


Troubleshooting
-------------
If you encounter an error while running chartio_setup, the file
    /tmp/chartio_error.html
may contain details on what went wrong. In any event, please feel free
to contact support.

In addition, the log file
    ~/.chartio.d/logs/chartio_connect.log
contains information about the chartio_connect process.


Documentation
-------------
Further documentation may be found at http://chart.io/


Package Contents
----------------
    chartio_setup
        The configuration wizard

    chartio_connect
        A script to keep the SSH tunnel alive


Notable Changes
---------------
Version 1.1.17
- Change domain to chartio.com

Version 1.1.16
- add option to post error information to Chartio

Version 1.1.13
- add Oracle support

Version 1.1.12
- check Chartio version

Version 1.1.7
- permit manual entry of database and readonly user/password

Version 1.1.6
- grant 'SHOW VIEW' access when creating mysql read-only database user
- bug fix for handling of blank database administrator password
