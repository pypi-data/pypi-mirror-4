# -*- coding: utf-8 -*-

"""
Created on 2012-11-26
:summary:
:author: Andreas Kaiser (disko)
"""

from deform import Form
from deform.widget import TextInputWidget
from pkg_resources import resource_filename

try:
    from js.dynatree import dynatree
    use_fanstatic = True
except:
    use_fanstatic = False


class DynatreeWidget(TextInputWidget):
    """
    DynatreeWidget
    """

    #: r/w template
    template = 'dynatree'
    #: r/o template
    readonly_template = 'readonly/dynatree'
    values = ()
    #: URL for the server side REST API
    api_url = ''
    #: automatically collapse siblings when a node is expanded
    autoCollapse = 'true'
    #: set focus to first child, when expanding or lazy-loading
    autoFocus = 'true'
    #: 0: quiet, 1: normal, 2: debug
    debugLevel = 0

    def serialize(self, field, cstruct, readonly=False):
        """
        Default :method:`deform.widget.HiddenWidget.serialize` method with
        optional fanstatic support.
        """

        if use_fanstatic:
            dynatree.need()

        return TextInputWidget.serialize(self, field, cstruct, readonly=readonly)


def includeme(config):

    loader = Form.default_renderer.loader
    loader.search_path = (
        resource_filename(
            'deform_widget_dynatree',
            'templates'
        ),
    ) + loader.search_path
