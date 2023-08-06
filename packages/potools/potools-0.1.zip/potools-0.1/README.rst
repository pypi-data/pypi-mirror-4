potools
=======

This package contains command line tools to help manage translations.

* *podiff*: Shows the differences between two po files. It only cares about msgid and msgstr, not about position in the file, comments, etc. You can also specify a version control repository with which to compare a file with.

* *pogetnew*: Compares two po files and return all new entries that need to be translated. Output is printed to stdout, in the format as a valid po file, so that it can be sent to translator.

* *pocheck*: Checks the pot/po file for smells. 

Installation
============

Simply run::
    
    pip install potools

or if you are using easy_install::
    
    easy_install potools

Buildout users can add the following part to their buildouts::

    [script]
    recipe = zc.recipe.egg
    eggs = potools 
