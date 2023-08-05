=======================
Qooxdoo Buildout Recipe
=======================

Buildout recipe, that runs Qooxdoo generator script. It requires Qooxdoo SDK to run.

Parameters
==========

* **script** - Name of the written script. Defaults to part name.
* **commands** - Command executed by the generator. It must be exported by project config. If empty, either command-line arguments or default command from ``config.json`` will be used.
* **config** - Path to the project configuration file, or directory containing ``config.json`` file.
* **qooxdoo-sdk** - Path to the qooxdoo sdk. Fallbacks to ``${buildout:qooxdoo-sdk}`` variable. SDK must exist. Corresponds to ``QOOXDOO_PATH`` macro.
* **cache** - Qooxdoo cache path. If empty, ``${buildout:cache-directory}`` will be used. If neither is specified, Qooxdoo default will be used. It corresponds to ``CACHE`` macro.
* **let** - Qooxdoo environmental variables, as are under ``"let"`` keyword in ``config.json``. It should be in ``key:value`` format since Qooxdoo generator expects it. It may contain multiple pairs. Optional.
* **remove-dirs** - Directories that should be removed on script execution. Path is relative to buildout root. Optional.
* **create-dirs** - Directories that should be created on script execution. Path is relative to buildout root. Useful for jobs that require some path to exist. Optional.
* **clean-dirs** - Directories which contents should be removed on script execution. Path is relative to buildout root. Useful for jobs that require some path to exist and yet you want their content to be recreated every time (like images creation). Optional.

Options ``commands`` and ``config`` can contain multiple entries. Projects are then built sequentially for each project,
with each command executed as standalone process.

When ``commnads`` is ommited and command-line arguments are used as commands, they are split and executed sequentially
as well. Therefore you can run e.g. ``translate lint build`` in one go, which generator itself does not support.

Example
=======

Example buildout.cfg::

    [buildout]
    parts =
      qooxdoo-sdk
      translate
      qx

    qooxdoo-sdk = ${qooxdoo-sdk:destination}
    cache-directory = cache

    [qooxdoo-sdk]
    recipe = hexagonit.recipe.download
    url = http://downloads.sourceforge.net/project/qooxdoo/qooxdoo-current/2.1/qooxdoo-2.1-sdk.zip
    destination = qooxdoo-sdk
    strip-top-level-dir = true

    [translate]
    recipe = mdvorak.recipe.qooxdoo
    commands = translation
    config = src/config.json

    [qx]
    recipe = mdvorak.recipe.qooxdoo
    config = src/config.json

You can then execute translation job with ``./bin/translate``, or any command using ``./bin/qx``. Try ``./bin/qx info``
to see how is Qooxdoo configured.

Create scripts for any jobs (and job sequences) you want.
