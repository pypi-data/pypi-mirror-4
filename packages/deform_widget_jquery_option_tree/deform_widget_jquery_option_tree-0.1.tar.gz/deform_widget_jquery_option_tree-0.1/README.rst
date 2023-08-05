This package makes
`jQuery Option Tree <http://code.google.com/p/jquery-option-tree/>`_
available as a `deform form library <http://pypi.python.org/pypi/deform/>`_
widget.  jQuery Option Tree converts a JSON option tree into dynamically
created <select> elements allowing you to choose one nested option from the
tree.

Currently only one feature for a very specific use case is implemented,
hierarchical browsing from a data structure like this::

    key     value
    ---     -----
    1       Option 1
    11      Suboption 1.1
    111     Subsubption 1.1.1
    112     Subsubption 1.1.2
    12      Suboption 1.2
    2       Option 2
    21      Suboption 2.1
    22      Suboption 2.2
    3       Option 3

The implementation is currently limited to 1 character == 1 level as keys.
This is suitable for hierarchical selections from standards like
`ISCO08 <http://en.wikipedia.org/wiki/International_Standard_Classification_of_Occupations>`_ or
`NACE Rev. 2 <http://en.wikipedia.org/wiki/Statistical_classification_of_economic_activities_in_the_European_Community>`_

See the included demo application for details.

Contributions
-------------

Contributions are welcome, especially if you want to add support for
more generic data structures and/or configurable options for the plugin.
