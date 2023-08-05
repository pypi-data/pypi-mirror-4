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

This is suitable for hierarchical selections from standards like
`ISCO08 <http://en.wikipedia.org/wiki/International_Standard_Classification_of_Occupations>`_ or
`NACE Rev. 2 <http://en.wikipedia.org/wiki/Statistical_classification_of_economic_activities_in_the_European_Community>`_

The implementation currently requires the data to be exposed by a REST service
with 2 endpoints that are reachable via a common base URL (the ``json_url``
option of the widget):

    -   json_url has to return the top level key/value pairs

    -   json_url with the GET parameter ``ìd`` has to return the child elements
        for the given id.

    -   json_url + '/<id>/lineage' has to return the lineage of IDs from root to
        leaf for the given <id>.

Examples::

    json_url = '/api/classifications/nace_rev2'

    # GET call to '/api/classifications/nace_rev2'
    # has to return a structure like this:
    {
        A: "LAND- UND FORSTWIRTSCHAFT, FISCHEREI",
        B: "BERGBAU UND GEWINNUNG VON STEINEN UND ERDEN",
        C: "VERARBEITENDES GEWERBE/HERSTELLUNG VON WAREN"
    }

    # GET call to '/api/classifications/nace_rev2?id=A'
    # has to return a structure like this:
    {
        A01: "Landwirtschaft, Jagd und damit verbundene Tätigkeiten",
        A02: "Forstwirtschaft und Holzeinschlag",
        A03: "Fischerei und Aquakultur"
    }

    # GET call to '/api/classifications/nace_rev2/Q8690/lineage'
    # has to return a structure like this:
    ["Q", "Q86", "Q869", "Q8690"]

See the included demo application for details.

Contributions
-------------

Contributions are welcome, especially if you want to add support for
more generic data structures and/or configurable options for the plugin.
