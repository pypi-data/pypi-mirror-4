trash-cli - Command Line Interface to FreeDesktop.org Trash.
============================================================

|Donate|_

trash-cli trashes files recording the original path, deletion date, and 
permissions. It uses the same trashcan used by KDE, GNOME, and XFCE, but you 
can invoke it from the command line (and scripts).

It provides these commands::

    trash-put           trashes files and directories. 
    trash-empty         empty the trashcan(s).
    trash-list          list trashed file.
    restore-trash       restore a trashed file.

Usage
-----

Trash a file::

    $ trash-put foo

List trashed files::

    $ trash-list
    2008-06-01 10:30:48 /home/andrea/bar
    2008-06-02 21:50:41 /home/andrea/bar
    2008-06-23 21:50:49 /home/andrea/foo

Search for a file in the trashcan::

    $ trash-list | grep foo
    2007-08-30 12:36:00 /home/andrea/foo
    2007-08-30 12:39:41 /home/andrea/foo

Restore a trashed file::
    
    $ restore-trash
    0 2007-08-30 12:36:00 /home/andrea/foo
    1 2007-08-30 12:39:41 /home/andrea/bar
    2 2007-08-30 12:39:41 /home/andrea/bar2
    3 2007-08-30 12:39:41 /home/andrea/foo2
    4 2007-08-30 12:39:41 /home/andrea/foo
    What file to restore [0..4]: 4
    $ ls foo
    foo

Remove all files from the trashcan::

    $ trash-empty

Remove only the files that have been deleted before <days> ago::
    
    $ trash-empty <days>

Example::

    $ date
    Tue Feb 19 20:26:52 CET 2008
    $ trash-list
    2008-02-19 20:11:34 /home/einar/today
    2008-02-18 20:11:34 /home/einar/yesterday
    2008-02-10 20:11:34 /home/einar/last_week
    $ trash-empty 7
    $ trash-list
    2008-02-19 20:11:34 /home/einar/today
    2008-02-18 20:11:34 /home/einar/yesterday
    $ trash-empty 1
    $ trash-list
    2008-02-19 20:11:34 /home/einar/today

Using it as 'rm' alias
----------------------

`trash-put` accept all the options that GNU `rm` does, if you prefer (I don't)
you can set up this alias in your .bashrc::

    alias rm='trash-put'

At the present the semantic of trash-put is sligthly different from the one of
`rm`, for example, while `rm` requires `-R` for deleting directories 
`trash-put` does not. This may change in future.

Keep in mind that Bash aliases are used only in interactive shells, so using 
this alias should not interfere with scripts that expects to use `rm`.

Installation (the easy way)
---------------------------

Requirements:

 - Python 2.7 
 - setuptools (use `apt-get install python-setuptools` on 
   Debian)

Installation command::
 
    easy_install trash-cli

Installation from sources
-------------------------

::

    # grab the latest sources
    wget https://github.com/andreafrancia/trash-cli/tarball/master 
    
    # unpack and install
    tar xfz andreafrancia-trash-cli-xxxxxxxx.tar.gz
    cd andreafrancia-trash-cli-xxxxxxxx
    sudo python setup.py install

Bugs and feedback
-----------------

If you discover a bug please report it to:

    https://github.com/andreafrancia/trash-cli/issues

You can reach me via email at me@andreafrancia.it .  For twitter use 
@andreafrancia or #trashcli

Development
-----------

Environment setup::

    virtualenv env --no-site-packages
    source env/bin/activate
    pip install -r requirements-dev.txt

Running tests::

    nosetests unit_tests           # run only unit tests
    nosetests integration_tests    # run all integration tests
    nosetests -A 'not stress_test' # run all tests but stress tests
    nosetests                      # run all tests

Check the installation process before release::

    python check_release_installation.py

Profiling unit tests::

    pip install gprof2dot
    nosetests --with-profile --profile-stats-file stats.pf --profile-restrict=unit_tests unit_tests
    gprof2dot -w  -f pstats stats.pf | dot -Tsvg >| stats.svg
    open stats.svg

.. |Donate| image:: https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif
.. _Donate: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=93L6PYT4WBN5A

