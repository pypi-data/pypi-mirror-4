TODO List
=========

In decreasing order of importance.


Write tests!
------------

Self-explanatory.


Add "no argument" option to both label and goto cli
---------------------------------------------------

The expected result of a call to `label` or `goto` without arguments is to
print all labels and paths. It is not happening right now because I do not
know how to add to argparse a "no argument" option.


Make the installation fully automatic
-------------------------------------

Currently, the user need to run three commands to install `goto`. This is a
error prone approach. Merge all commands to `pip install goto-dir`.


Write a man page
----------------

Self-explanatory.


Suggestion: Highlight label names in error messages
---------------------------------------------------

In error messages like `workspace is not a valid label.` would be nice
to have the word "workspace" in another color to ease the reading.
