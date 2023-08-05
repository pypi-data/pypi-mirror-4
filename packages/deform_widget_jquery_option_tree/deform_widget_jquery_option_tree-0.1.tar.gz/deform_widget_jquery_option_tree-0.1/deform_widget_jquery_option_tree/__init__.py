# -*- coding: utf-8 -*-
"""
Created on 2012-10-18 17:47
:summary:
:author: Andreas Kaiser (disko)
"""

import json
from colander import null
from deform import Form
from deform.compat import string_types
from deform.widget import HiddenWidget
from pkg_resources import resource_filename

try:
    from js.jquery_option_tree import jquery_option_tree
    use_fanstatic = True
except:
    use_fanstatic = False


def includeme(config):

    loader = Form.default_renderer.loader
    loader.search_path = (
        resource_filename(
            'deform_widget_jquery_option_tree',
            'templates'
        ),
    ) + loader.search_path


class JqueryOptionTreeWidget(HiddenWidget):

    template = 'jquery_option_tree'
    readonly_template = 'readonly/jquery_option_tree'
    values = ()
    json_url = ''

    def __init__(self, **kw):

        super(JqueryOptionTreeWidget, self).__init__(**kw)

        if use_fanstatic:
            jquery_option_tree.need()
