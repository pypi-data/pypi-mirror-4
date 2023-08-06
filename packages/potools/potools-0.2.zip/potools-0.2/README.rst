potools
=======

This package contains command line tools to help manage translations.

* *podiff*: Shows the differences between two po files. It only cares about the default value, msgid and msgstr, not about position in the file. You can also specify a version control repository with which to compare a file with.

* *pogetnew*: Compares two po files and return all new entries that need to be translated. Output is printed to stdout, in the format as a valid po file, so that it can be sent to translator.

* *pocheck*: Checks the pot/po file for smells. 
    * The `Translate Toolkit`_ provides a similar tool called `pofilter`_. Pocheck aims to not duplicate any of the functionality already in *pofilter*.

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

One-liners
==========

podiff
------

* Diff all po files in a git repository, with the last committed versions::

    find -name "*.po" -exec podiff --vcs git $(git remote -v | awk 'BEGIN {} NR ==2 {print substr ($2, 1)}') {} \; 

.. _`Translate Toolkit`: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/
.. _`pofilter`: http://translate.sourceforge.net/wiki/toolkit/pofilter
