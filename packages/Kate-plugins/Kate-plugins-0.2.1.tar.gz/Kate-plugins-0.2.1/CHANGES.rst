Releases
========

0.2.1  (2013-03-11)
-------------------

* This release is out of support
* Now works from pypi
* Improvement to pep8 checker

0.2.0  (2013-02-12)
-------------------

* Fix an error in the Close Template tag (django)
* Details to the JSON plugin
* Improve in the js autocomplete generator


0.1.9  (2013-02-06)
-------------------

* These changes are **backwards incompatibles**.
* Adapt the plugins to the last Kate (2013-02-06)
* Fix a little error in the pep8 plugin
* Improve the JSON plugin

0.1.8  (2012-09-02)
-------------------

* Fix an error in jQuery autocomplete and js autocomplete, broken `in this commit <https://github.com/goinnn/Kate-plugins/commit/de7453f94341f84f5fab36d277a7f8383e961121>`_
* Add try/except, if the user has not simplejson egg installed


0.1.7  (2012-09-02)
-------------------

* Adapt the code to the last version of pyplete. Now the python autocomplete plugin can autocomplete the relative imports, something like this:

::

   from models import MyModel # from the same directory of the models.py

And this:

::

   from .models import MyModel # from the same directory of the models.py


0.1.6  (2012-08-18)
-------------------

* Fix for autocomplete in the last KDE 
* Restructuring of menus
* Refactor
* Thank you to `Jeroen van Veen <https://github.com/phrearch>`_ to the changes


0.1.5  (2012-07-09)
-------------------

* Liberate `PyPlete <http://pypi.python.org/pypi/pyplete>`_ (You need install this egg if you want python autocomplete)
* Add Copyright


0.1.4  (2012-06-15)
-------------------

* Detail to jQuery autocomplete. This did not accept something like this: jQuery("a.class-with-dash")


0.1.3  (2012-04-24)
-------------------

* I forgot the block_plugins file.... o_O

0.1.2  (2012-04-22)
-------------------

* Insert separators in the menu, before and after, of the plugins
* Add Close Template tag plugin
* Add Template block plugin


0.1.1  (2012-03-17)
-------------------

* Created a menu structure to the plugins, before they were all in edit menu
* Refactor an clean the code, if you insert a text with XXX, the cursor move here
* Fix a little error in the jQuery plugin regex
* Fix a little error in the python plugin, when the lines contains ";"

0.1.0  (2012-03-15)
-------------------

* A new settings to ignore pep8 errors
* Now is possible move between various errors in the same line
* Fix jslint errors line number
* Fix callRecursive error, when to call the plugin with text in this line
* Fix a little error in autocomplete

0.0.9  (2012-03-12)
-------------------

* Add jQuery autocomplete plugin
* Add XML pretty plugin
* Add call recursive plugin

* Title in the autocompletes
* Fix some error in js autocomplete
* Now the python autocomplete can depend of the session

* The checker plugins move to the first error, from position, when they are invoked
* Remove old popups in check plugins

* Improvement in the usability of the template Django urls plugin and jQuery ready plugin
* Other settings: PYTHON_AUTOCOMPLETE_ENABLED, JAVASCRIPT_AUTOCOMPLETE_ENABLED, JQUERY_AUTOCOMPLETE_ENABLED, CHECKALL_TO_SAVE
* Refactor: Rename the utils file to kate_core_plugins, removing unnecessary code


0.0.8  (2012-03-03)
-------------------

* Usability improvements in check plugins

0.0.7  (2012-03-02)
-------------------

* Fix some errors of the 0.0.6 version (checker plugins)
* Fix a error of JSON autocompletion
* Update the readme

0.0.6  (2012-03-02)
-------------------

* Python parse syntax plugin
* PEP8 checker plugin
* PyFlakes checker plugin
* JSLint checker plugin
* Settings to the kate actions: texts, short cuts, menus and icons

0.0.5  (2012-02-28)
-------------------

* Cleaning code
* Fix little error in preatty JSON. The quotes should be " instead of '
* Fix some other error
* Refactored autocomplete plugin to python
* Created a pyplete, a generic module to autocompletion in python
* Fix a in the code to detect the class has a error (insert init plugin, insert super plugin)


0.0.4  (2012-02-20)
-------------------

* Fix a error in autocomplete, if the line contains "and" or "or" 
* Improvement in the performance in the python autocompletation
* Abstraction of Autocomplete. Create a Abstract class
* Create a AbstractJSONFileCodeCompletionModel. Only autocompletion creating a json file
* Create a static autocompletation to javascript

0.0.3  (2012-02-02)
-------------------

* Fix some errors to autocomplete
* Icons different to packages and modules
* Usability in the autocomplete:
* The popup that say "Syntax error" only show if the autocomplete is not manual
* The python autocomplete, only works if the file ends with ".py", ".pyc" or it is not saved


0.0.2  (2012-02-01)
-------------------

* Autocomplete to python (second version)

0.0.1  (2012-01-29)
-------------------

* Autocomplete to python (first version)
* ipdb, init, super, urls, form, model, ready, json plugin
