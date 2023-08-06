===========
Description
===========

Monitoring hard discs in a raid system on linux servers. Raid Guard runs as a 
daemon and will send mails on specific events.

**License**

    MIT License

**Notes**

    * Only tested on a linux server

========
Features
========

    * runs as a daemon.
    * send a mail if a hard drive loss.
    * setup via configuration file.

============
Installation
============

**Dependences**

    * deiman (https://pypi.python.org/pypi/deiman/)
    * iniparse (https://pypi.python.org/pypi/iniparse/)

**Installation / Deinstallation**

    *with pip*
        
        ::
        
            pip install raid-guard
    
            pip uninstall raid-guard


    *or setup.py*

        1. Unpack your package.
        2. Open a terminal and change to the folder which contains the setup.py and type

        ::

            python setup.py install
   
=====
Setup
=====
    
    * edit the /usr/share/raid_guard/raid_guard.ini an copy it to /root/.raid_guard.ini
      or start the prog the first time and the ini file will copied automaticly to root.
    * Add an entry into the /etc/rc.local file: /usr/local/bin/raid_guard start

=====
Usage
=====

    *raid_guard [options]*
    
        options are: start, stop, status, help, test, logfile
    
=====
Hints
=====

    * The logfile is stored at /var/log/raid_guard.log