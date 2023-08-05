# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
"""
The basic premise is that lizard-structure only *shows* the application's
structure. There are no edit actions, so no POST/PUT/DELETE: only GET.

There are several basic ways to deal with naming the views. Especially when
you also want POST/PUT/DELETE, having both ``ObjectList`` and ``ObjectDetail``
makes sense. But we don't need that. What's most interesting are the lists,
these are also often the most effective. You don't want to have to grab
handfuls of URLs before you can render a page. You want the most useful data
right away. So on an :ref:`application` page, you want a list of projects. On
a :ref:`project` page, a list of layers. And so on.

We deemed it more useful to call the view with the list of projects the
application view, though. An application *is* a list of projects, so it makes
sense that way.

But: a project also has information on itself, as has a project, etc.

"""
from __future__ import unicode_literals

# from django.core.urlresolvers import reverse
# from django.utils.translation import ugettext as _
from rest_framework.response import Response
from rest_framework.views import APIView


class ApplicationView(APIView):
    """
    Information about the application and its list of projects.
    """
    pass


class ProjectView(APIView):
    """
    Information about the project and its list of layers.
    """
    # Representation: some sort of sidebar structure/tree with menuitems or
    # workspaceacceptables.
    pass


class LayerView(APIView):
    """
    Information about the layer and its list of features.
    """
    # Representations: geojson, WMS, etc.
    pass


class FeatureView(APIView):
    """
    Information about the feature and most importantly its representations.
    """
    # Representations! flot, png graph, html, csv, etc.
    pass
