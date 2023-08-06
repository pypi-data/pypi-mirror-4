Push (Markdown) to wordpress
============================

**currently basic functionality**

| A simple, python based, commandline wordpress blogging tool.
| A commandline wrapper to publishing with
`python-markdown <https://github.com/waylan/Python-Markdown>`__

Version
-------

`Version <Version.md>`__

Techonology
-----------

Using:

1. `python-wordpress-xmlrpc <https://github.com/maxcutler/python-wordpress-xmlrpc>`__
2. `python-markdown <https://github.com/waylan/Python-Markdown>`__

using wordpress `XML-RPC
Api <http://codex.wordpress.org/XML-RPC_WordPress_API>`__ to drive
wordpress.

Installing
----------

**The short way**: Straight from the cheeseshop

::

    pip install push_to_wordpress

**The long way**:

::

    git clone git://github.com/alonisser/PushToWordpress.git

    cd PushToWordpress
    python setup.py install #(If that doesn't work you should run the build command first)

Usage:
------

Current and quite basic:

::

    presser --title optionaltitle --posts inputfile.md anotherinputfile

where there is a config.ini file with wordpress blog connection details
in the same folder.

**`Full command line options and flags <usage.txt>`__**

| Simple isn't it? going to be simpler soon..
| currently can't handle media files with the posts (but check the TODO
section for more info about that). Don't forget to enter your wordpress
blog config in the config.ini file (look at configdemo.ini for
inspiration)

License
-------

see **`License <License.md>`__**

TODO or "How can I help or contribute":
---------------------------------------

check our `TODO <TODO.md>`__

Notice:
-------

for older wordpress installs you should enable `enable the XML-RPC
api <http://codex.wordpress.org/XML-RPC_Support>`__ in later versions
it's enabled by default.
