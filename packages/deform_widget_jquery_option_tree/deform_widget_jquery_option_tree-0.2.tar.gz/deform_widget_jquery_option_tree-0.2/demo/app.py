# -*- coding: utf-8 -*-
"""
Created on 2012-10-19 16:34
:summary: A Pyramid application that demonstrates the widget.

          Instructions:

            1. pip install Pyramid
            2. pip install deform_widget_jquery_option_tree
            3. python app.py

          An HTTP server will listen on port 6543: http://0.0.0.0:6543
:author: Andreas Kaiser (disko)
"""

from colander import Schema
from colander import SchemaNode
from colander import String
from deform import Form
from deform import ValidationFailure
from deform_widget_jquery_option_tree import JqueryOptionTreeWidget
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.view import view_defaults


class DemoSchema(Schema):
    """
    :summary: A simple demo schema with a single node.
    """

    demo = SchemaNode(
        String(),
        missing="",
        widget=JqueryOptionTreeWidget(
            json_url="/json"
        )
    )


@view_defaults(route_name="root",
               renderer="deform_widget_jquery_option_tree:../demo/index.pt")
class Views(object):
    """
    :summary: A class containing all view callables.
    """

    def __init__(self, request):
        """
        :summary: Constructor
        :param request: The request object
        :type request: pyramid.request.Request
        """

        self.request = request
        self.schema = DemoSchema()
        self.form = Form(self.schema, buttons=['submit', ])

    @view_config(request_method="GET")
    def get(self):
        """
        :summary: Default route with request method GET.
                  The form will be displayed without a preselected value.
        :result: A dictionary containing the rendered view.
        :rtype: dict
        """

        return {
            "form": self.form.render(),
        }

    @view_config(request_method="POST")
    def post(self):
        """
        :summary: Default route with request method POST.
                  The form will be displayed with the submitted value preselected.
        :result: A dictionary containing the rendered view.
        :rtype: dict
        """

        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = self.form.validate(controls)
            except ValidationFailure, e:
                return {
                    'form': e.render()
                }

        return {
            "form": self.form.render(appstruct),
        }

    @view_config(route_name="json", renderer="json")
    def json(self):
        """
        :summary: JSON structure queried by the widget.
        :result: Dictionary with <option value>: <option title> elements.
        :rtype: dict
        """

        if 'id' in self.request.GET:
            if self.request.GET['id'] == '1':
                return {
                    '11': "Option 1.1",
                    '12': "Option 1.2",
                }
            elif self.request.GET['id'] == '2':
                return {
                    '21': "Option 2.1",
                    '22': "Option 2.2",
                }
            if self.request.GET['id'] == '11':
                return {
                    '111': "Option 1.1.1",
                    '112': "Option 1.1.2",
                }
            else:
                return {}

        return {
            '1': "Option 1",
            '2': "Option 2",
            '3': "Option 3",
        }


def make_app(global_config, **settings):
    """
    :summary: Initialize and configure the Pyramid application
    :result: A WSGI application
    """

    settings['pyramid.reload_templates'] = 'true'

    config = Configurator(settings=settings)

    config.include('deform_widget_jquery_option_tree')

    config.add_static_view('static', 'deform_widget_jquery_option_tree:static/')
    config.add_route('root', '/')
    config.add_route('json', '/json')

    config.scan()

    return config.make_wsgi_app()


if __name__ == '__main__':

    from waitress import serve

    serve(make_app({}), port=6543, expose_tracebacks=True)
