current/unstable
----------------

v0.2.0
------

* `goto` without arguments shows all existing labels and paths

* `label` without arguments insert the current path with his inner folder as label

* `--remove` is now `--delete`

* `label` now has short arguments:

  * `-d` is equals to `--delete`

  * `-r` is equals to `--replace`

* Reject labels bigger than 32 characters.

* Reject labels that are not valid filenames (except whitespaces).

* Slugify (by replace whitespace blocks by underscores) automatically created labels.

* Fix bug that prevents `goto` to cd into a path with whitespaces.

* Fix bug that prevents `goto` and `label` to handle non ascii paths.

* Auto remove "dangling" label when the user tries to goto to it.

* Application is now compatible with Mac OS

v0.1.1
------

* Change install command from distutils to setuptools to allow us to extend the installation procedure.

v0.1.0
------

* Initial public version.