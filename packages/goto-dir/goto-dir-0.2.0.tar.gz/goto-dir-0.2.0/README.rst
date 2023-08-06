goto project - easy'n'fast cd'ing
=================================

Tired of typing a lot to get where the fun is happening? `goto` was made for you!


Instalation
-----------

Method 1::

    $ pip install goto-dir

Method 2::

    $ git clone git://github.com/pauloborges/goto.git
    $ cd goto && [sudo] python setup install


goto
----

The `goto` command is used to navigate through shortcuts.

Using it without parameters returns a list of all currently labels::

    $ goto
    home    /home/borges
    ws      /home/borges/workspace
    docs    /home/borges/Documents

When you pass a label name, `goto` changes the current directory::

    /old/dir$ goto home
    /home/borges$

But if the label does not exists, an error is thrown::

    $ goto connman
    connman is not a valid label.


label
-----

The `label` command is used to save shortcuts to directories.

When you pass a simple string, the current directory is saved::

    /home/borges/Downloads$ label downloads
    downloads label points to /home/borges/Downloads.

Using it without parameters saves the current directory using the inner folder as label::

    /path/to/something$ label
    something label points to /path/to/something.

If the label already exists and points to another directory, an error is thrown::

    /home/borges/workspace$ label ws
    ws label already exists. Use --replace.

The replacement can be ensured by `-r|--replace`::

    /home/borges/my_new_workspace$ label -r ws
    ws label now points to /home/borges/my_new_workspace.

You can delete a label using `-d|--delete`::

    $ label -d docs
    docs label was deleted.

But if the label does not exists::

    $ label -d connman
    connman is not a valid label.


.goto file
----------

All label information are stored in `~/.goto`. See an example::

    $ cat ~/.goto
    [labels]
    home = /home/borges
    ws = /home/borges/workspace
    docs = /home/borges/Documents


License
-------

See `LICENSE` file.
