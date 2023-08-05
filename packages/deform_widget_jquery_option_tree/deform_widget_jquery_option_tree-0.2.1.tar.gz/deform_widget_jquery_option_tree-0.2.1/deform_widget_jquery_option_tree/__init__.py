# -*- coding: utf-8 -*-
"""
Created on 2012-10-18 17:47
:summary:
:author: Andreas Kaiser (disko)
"""

from deform import Form
from deform.widget import HiddenWidget
from pkg_resources import resource_filename

try:
    from js.jquery_option_tree import jquery_option_tree
    use_fanstatic = True
except:
    use_fanstatic = False


class JqueryOptionTreeWidget(HiddenWidget):

    template = 'jquery_option_tree'
    readonly_template = 'readonly/jquery_option_tree'
    values = ()
    json_url = ''

    def serialize(self, field, cstruct, readonly=False):

        if use_fanstatic:
            jquery_option_tree.need()

        return HiddenWidget.serialize(self, field, cstruct, readonly=readonly)


def includeme(config):

    loader = Form.default_renderer.loader
    loader.search_path = (
        resource_filename(
            'deform_widget_jquery_option_tree',
            'templates'
        ),
    ) + loader.search_path
