======================
brodul.recipe.template
======================

brodul.recipe.template is a fork of amplecode.recipe.template, a Buildout recipe for generating files using Jinja2 templates. The recipe configures a Jinja2 environment, by default relative to the Buildout directory, allowing templates to extend and include other templates relative to the environment.

Downloads are available from pypi: http://pypi.python.org/pypi/brodul.recipe.template/

.. image:: https://secure.travis-ci.org/brodul/amplecode.recipe.template.png

Buildout Options
================

* template-file or input (required): One or more Jinja2 template file paths.
* target-file or output (required): One of more target file paths. The number of files must match the number of template files.
* base-dir: Base directory of the Jinja2 environment. Template file paths are relative to this directory. Default is the Buildout directory.
* target-executable: One or more boolean flags (yes|no|true|false|1|0) indicating the executability of the target files. If only one flag is given it is applied to all target files.
* eggs: Reserved for a list of eggs, conveniently converted into a pkg_resources.WorkingSet when specified
* jinja2_filters: custom filter functions separated by white-space

Additional options are simply forwarded to the templates, and options from all the other parts are made available through ``parts.<part-name>.<option-name>`` and ``parts[<part-name>][<option-name>]``.

Lists of Values
===============

It is possible for a recipe option to contain one or more values, separated by whitespace. A split filter is available for when you want to iterate over the whitespace separated values in your Jinja2 template::

  #!/bin/sh
  {% for cmd in cmds|split %}
     echo "{{ cmd }}"
  {% endfor %}

Minimal Example
===============

foo.txt is created from foo.txt.jinja2 without any extra options::

  [buildout]
  parts = foo

  [foo]
  recipe = brodul.recipe.template
  template-file = foo.txt.jinja2
  target-file = foo.txt

Larger Example
==============

foo.txt is created from myapp/foo.txt.jinja2, bar.sh is created from myapp/bar.sh.jinja2, the second will be executable, and both templates can utilize the additional options specified::

  [buildout]
  parts = foo

  [foo]
  recipe = brodul.recipe.template
  base-dir = myapp
  template-file =
      foo.txt.jinja2
      bar.sh.jinja2
  input =
      foo.txt
      bar.sh
  output =
      false
      true
  project_name = Another Example
  author = Me

  [bar]
  dashed-value = borg
  value = cash

foo.txt.jinja2:
::

  {{ parts.bar['dashed-value'] }}
  {{ parts.bar.value }}
  {{ author }}

.. note::
  
  `{{ parts.bar.dashed-value }}` won't work, but you can access it as a dict key.

Dashed value in the same part
=============================

If there is a dashed-value in brodul.recipe.template part and you would like to reference it, use:
::
  
  {{context['dashed-value']}}


Custom filters
==============

The filter function is located in the same directory as the buildout.cfg in a filter.py file. If you want to use more filters separate them with a white space. ::

  [buildout]
  parts = foo

  [foo]
  recipe = brodul.recipe.template
  input = foo.txt.jinja2
  output = foo.txt
  jinja2_filters = filter.bar


Changelog
=========

See the CHANGELOG file

License
=======

See the LICENSE file

Todo
====


Why this fork
=============

* there should be an input and output option in buildout (since the '-' in 'target-file' char is parsed by jinja2)
* custom filters support
