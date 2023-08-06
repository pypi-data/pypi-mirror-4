# -*- coding: utf-8 -*-
import pyramid.tweens
from zope.interface import implements, Interface
from por.dashboard.views import DefaultContext

DISCOVERY = False


def includeme(config):
    config.include('pyramid_skins')
    config.register_path("por.gdata:skins", discovery=DISCOVERY)

    config.add_view('por.gdata.views.clear_token', name='clear_gdata_token')
    config.add_view('por.gdata.views.add_token', name='add_gdata_token')
    config.add_view('por.gdata.views.generate_spreadsheet', name='generate_iteration', request_method="POST", permission='manage_iterations')
    config.add_view('por.gdata.views.activate_iteration', name='activate_iteration')
    config.add_tween('por.gdata.utils.fallback_tween_factory', over=pyramid.tweens.MAIN)

    config.add_route('view_iterations', '/view_iterations', factory='por.gdata.IterationContext')
    config.add_view('por.gdata.views.view_iterations', route_name='view_iterations', permission='view_iterations')

    config.add_route('manage_iterations', '/manage_iterations', factory='por.gdata.IterationContext')
    config.add_view('por.gdata.views.manage_iterations', route_name='manage_iterations', permission='manage_iterations')


class IIterationView(Interface):
    """Marker interface for iteration views"""


class IterationContext(DefaultContext):
    """Default context factory for Iteration views."""
    implements(IIterationView)

